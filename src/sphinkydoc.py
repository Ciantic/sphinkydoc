"""SphinkyDoc script"""
#from string import Template
import subprocess
import shutil
import logging
import optparse
import sys
import sphinkydocext
from sphinkydocext.directives.sphinkydoc import templating_environment
from distutils.dir_util import mkpath
import os

#from jinja2 import Template
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from jinja2.exceptions import TemplateError
import re

logging.basicConfig()
log = logging.getLogger("sphinkydoc")

DYNAMIC_SPHINX_DIR = 'data'
CONFIG_FILENAME = 'conf.py'
TEMP_CONFIGURATION_DIR = '_temp'

def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0, 
    update=0, verbose=0, skip_dirs=None, dry_run=0):
    """Copy an entire directory tree 'src' to a new location 'dst'.  
    Both 'src' and 'dst' must be directory names.  If 'src' is not a directory,
    raise DistutilsFileError.  If 'dst' does not exist, it is created with
    'mkpath()'.  The end result of the copy is that every file in 'src' is
    copied to 'dst', and directories under 'src' are recursively copied to
    'dst'.  Return the list of files that were copied or might have been copied,
    using their output name.
    
    The return value is unaffected by 'update' or 'dry_run': it is simply the
    list of all files under 'src', with the names changed to be under 'dst'.
    
    'preserve_mode' and 'preserve_times' are the same as for
    'copy_file'; note that they only apply to regular files, not to
    directories.  If 'preserve_symlinks' is true, symlinks will be copied as
    symlinks (on platforms that support them!); otherwise (the default), the
    destination of the symlink will be copied.
    
    'update' and 'verbose' are the same as for 'copy_file'.
    
    """
    from distutils.file_util import copy_file
    
    skip_dirs = skip_dirs or []
    
    if not dry_run and not os.path.isdir(src):
        log.error("cannot copy tree '%s': not a directory", src)
        sys.exit(0)
    try:
        names = os.listdir(src)
    except os.error, (errno, errstr):
        if dry_run:
            names = []
        else:
            log.error("error listing files in '%s': %s", src, errstr)
            sys.exit(0)
    if not dry_run:
        mkpath(dst)
    outputs = []
    for n in names:
        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)
        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name) #@UndefinedVariable
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name) #@UndefinedVariable
            outputs.append(dst_name)
        elif os.path.isdir(src_name) and \
            os.path.dirname(src_name) not in skip_dirs:
            
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode, 
                    preserve_times, preserve_symlinks, update, 
                    dry_run=dry_run))
        else:
            copy_file(src_name, dst_name, preserve_mode, 
                preserve_times, update, dry_run=dry_run)
            outputs.append(dst_name)
    
    return outputs
        
def template_dir(template_dir, file_substs=None, substs=None, dry_run=False):
    """Templates the directory using jinja2.
    
    All files inside template_dir which has ".template" in filename is 
    templated.
    
    :param template_dir: Path to directory of templating.
    :param file_substs: Dictionary of template substitions by filename relative 
        to templating directory
    :param substs: Base substitions for *all* templates.
    :param dry_run: Dry run, no harmful changes done.
    
    """
    log.info("Templating the directory: %s" % template_dir)
    substs = substs or {}
    file_substs = file_substs or {}
    
    template_dir = os.path.realpath(template_dir)
    
    def valid_template_filename(filename):
        return ".template" in filename and len(filename) > len(".template")
    
    template_env = templating_environment(template_dirs=[template_dir])
    
    # Loop through all files recursively in template directory
    for dirpath, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            # Is valid template
            if not valid_template_filename(filename):
                continue
            
            t_filepath = os.path.join(os.path.realpath(dirpath), filename)
            filepath = os.path.join(dirpath, filename.replace(".template", ""))
            
            # Move template to destination
            log.info("Moving '%s' to '%s' ..." % (t_filepath, filepath))
            if not dry_run:
                shutil.move(t_filepath, filepath)
               
            # Relative to template dir, convert to posix
            rel_filepath = filepath[len(template_dir)+1:].replace("\\", "/")
            
            # Read the file to template object
            try:
                t = template_env.get_template(rel_filepath)
            except TemplateError, te:
                log.exception(te)
                sys.exit(0)
            
            # Get template substitions
            s = {}
            s.update(substs)
            s.update(file_substs.get(rel_filepath, {}))
            
            # Try to template using substition
            try:
                tmp = t.render(s)
            except TemplateError, te:
                log.error(te)
            else:
                log.info("Writing the templated file to '%s'..." % rel_filepath)
                
                try:
                    if not dry_run:
                        f = open(filepath, 'w+')
                        f.write(tmp)
                        f.close()
                except:
                    log.exception("Template file '%s' is not writable..." % \
                                  filepath)
                    sys.exit(0)
    
    log.info("Directory templated.")

def _magic(filepath, template_file, context=None):
    """Turns file to reStructuredText literal file.
    
    """
    context = context or {}
    magic_name = os.path.basename(os.path.splitext(filepath)[0])
    
    context.update({
        'magic_name' : magic_name, 
        'magic' :  open(filepath, 'r').read(),
    })
    
    tenv = templating_environment()
    t = tenv.get_template(template_file)
    tc = t.render(context)
    
    f = open(filepath, 'w+')
    f.write(tc)
    f.close()
    
def magic(filepath):
    """Preprocesses magic files by sphinkydoc/magic.rst jinja2 template.
    
    :path filepath: Path to the magic file.
    
    """
    _magic(filepath, "sphinkydoc/magic.rst")

def magic_literal(filepath, header=None):
    """Turns file to reStructuredText literal file.
    
    :param filepath: Path to the file being mangled.
    :param header: Header for the created reStructuredText file, defaults to
        filename without extension.
    
    """
    
    if header is None:
        header = os.path.basename(os.path.splitext(filepath)[0])
    
    _magic(filepath, "sphinkydoc/magic_literal.rst", {'header' : header})

def generate_magic(magic_dir, dst_dir, ext='rst', magic_literals=None, 
                   dry_run=False):
    """Copies magic files from ``magic_dir`` to destination directory.
    
    Magic files are files such as INSTALL, COPYING, README, which contain 
    documentation worthy content outside docs directory.
    
    :param magic_dir: Directory where magic files reside.
    :param dst_dir: Destination directory where magic files are *copied*.
    :param ext: Enforce all magic files to be in this extension.
    :param magic_literals: Magic files that are treated as literal files.
    :param dry_run: Dry run only, no copying or other harmful changes.
    
    :returns: Dictionary of extensionless filenames to filename with extension. 
    
    """
    magic_literals = magic_literals or []
    
    dir_contents = os.listdir(magic_dir)
    magic_files = []
    for filename in dir_contents:
        if re.match("^[A-Z](\.[A-Za-z]+)?", filename):
            new_filename = filename
            # Add the extension if not there
            if not filename.endswith(ext):
                new_filename += '.%s' % ext

            filepath = os.path.join(magic_dir, filename)
            new_filepath = os.path.join(dst_dir, new_filename) 
            
            if not dry_run:
                shutil.copy(filepath, new_filepath)
                
            if filename in magic_literals:
                magic_literal(new_filepath)
            else:
                magic(new_filepath)
            
            new_filename_wo_ext = new_filename[:-len(ext)-1]
            
            magic_files.append(new_filename_wo_ext)
    
    return magic_files
                    
def run_sphinx_build(sphinx_conf_dir, dry_run=False, 
                     sphinx_build='sphinx-build.py'):
    """Runs the sphinx-build.py in given directory.
    
    :param sphinx_conf_dir: Configuration directory of sphinx.
    :param dry_run: Dry run, don't do the actual build.
    :param sphinx_build: Sphinx build script location, defaults to 
        'sphinx-build.py', which assumes that it is in path.
    
    """
    old_dir = os.getcwd()
    os.chdir(sphinx_conf_dir)
    cmd1 = ["python", sphinx_build, ".", "../html"]
    cmd2 = ["python", sphinx_build, ".", "../html"]
    log.info("Sphinx build, inside directory %s" % os.getcwd())
    log.info("Running sphinx-build (1): %s" % subprocess.list2cmdline(cmd1))
    # TODO: PERFORMANCE: One could implement generation in this point, so the
    # second pass would not be required...
    log.info("Running sphinx-build (2): %s" % subprocess.list2cmdline(cmd2))
    
    if not dry_run:
        subprocess.call(cmd1)
        subprocess.call(cmd2)
    
    os.chdir(old_dir)

if __name__ == '__main__':
    parser = optparse.OptionParser("""sphinkydoc.py <MODULE>, ...""")
    
    parser.add_option("-v", "--verbose",
                      dest="verbose", action="store_true", default=True) # TODO: Debug True, Prod False
    parser.add_option("-n", "--dry-run", 
                      dest="dry_run", action="store_true", default=False)
    parser.add_option("-o", "--output-dir",
                      dest="output", default=os.getcwd())
    parser.add_option("-b", "--sphinx-build-py",
                      dest="sphinx_build", default="sphinx-build.py")
    parser.add_option("-t", "--sphinx-template-dir",
                      dest="sphinxtemplate_dir", default='')
    parser.add_option("-s", "--script",
                      dest="scripts", action="append", default=[])
    parser.add_option("", "--no-validation",
                      dest="validate", action="store_false", default=True)
    parser.add_option("", "--magic-dir",
                      dest="magic_dir", default="../")
    parser.add_option("-l", "--magic-literal",
                      dest="magic_literals", action="append", 
                      default=['COPYING', 'COPYING.LESSER'])
    try:
        (options, modules) = parser.parse_args()
    except:
        parser.print_usage()
        sys.exit(0)
        
    sphinx_project = '%s.__project__' % modules[0]
    sphinx_copyright = '%s.__copyright__' % modules[0]
    sphinx_version = '%s.__version__' % modules[0]
    sphinx_release = '%s.__release__' % modules[0]
    
    # Be verbose if on dry run
    if options.verbose or options.dry_run:
        log.setLevel(logging.INFO)
    
    # Sphinx configuration template directory 
    sphinxtemplate_dir = options.sphinxtemplate_dir or \
                         os.path.join(os.path.dirname(sphinkydocext.__file__),
                                          DYNAMIC_SPHINX_DIR)
    
    log.info("Creating documentation to "
             "directory '%(dir)s' ..." % {'dir': options.output })
    
    # Temp directory inside the docs
    temp_dir = os.path.join(options.output, TEMP_CONFIGURATION_DIR)
    magic_dir = os.path.realpath(options.magic_dir)
    
    # Remove old temp directory
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    
    # Copy the template directory to temp directory
    copy_tree(sphinxtemplate_dir, temp_dir, dry_run=options.dry_run)
    
    # Generate magic files
    magic_files = generate_magic(magic_dir, temp_dir, 
                                 magic_literals=options.magic_literals,
                                 dry_run=options.dry_run)
        
    # Template the temp directory
    template_dir(temp_dir, file_substs={
            'conf.py' : {
                'project' : sphinx_project,
                'copyright' : sphinx_copyright,
                'version' : sphinx_version,
                'release' : sphinx_release,
            }
        }, 
        substs={
            'magic_files' : magic_files,
            'scripts' : map(os.path.realpath, options.scripts),
            'modules' : modules,
        }, dry_run=options.dry_run)
    
    # Validates the conf.py
    if options.validate:
        log.info("Validating sphinx configuration file (using execfile)...")
        conf_file = os.path.join(temp_dir, CONFIG_FILENAME)
        try:
            execfile(conf_file)
        except Exception, e:
            log.exception("Unable to validate Sphinx configuration file: %s" % e)
            sys.exit(0)
    
    run_sphinx_build(temp_dir, sphinx_build=options.sphinx_build)