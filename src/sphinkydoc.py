"""SphinkyDoc script"""

DESCRIPTION = """Sphinx automated documentation generator and builder script.
Main purpose is to generate documentation for small projects, which usually does
not require external written documents."""

# Pylint-disable settings ----------------
# Todo messages:
#     pylint: disable-msg=W0511

from jinja2.exceptions import TemplateError
from sphinkydocext.directives.sphinkydoc import templating_environment
from sphinkydocext.utils import copy_tree
import logging
import optparse
import os
import shutil
import sphinkydocext
import subprocess
import sys

logging.basicConfig()
log = logging.getLogger("sphinkydoc")

DYNAMIC_SPHINX_DIR = os.path.join(os.path.dirname(sphinkydocext.__file__), 
                                  'data')
CONFIG_FILENAME = 'conf.py'
TEMP_CONFIGURATION_DIR = '_temp'

def template_dir(template_dir, file_substs=None, substs=None, dry_run=False):
    """Templates the directory using Jinja2.
    
    All files inside template_dir which has ".template" in filename is 
    templated using Jinja2 and the word ".template" is removed from filename.
    
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
        """Check that filename is valid templating filename.
        
        Currently checks that ".template" is in filename, and that filename
        is not exactly ".template".
        
        """
        return ".template" in filename and len(filename) > len(".template")
    
    template_env = templating_environment(template_dirs=[template_dir])
    
    # Loop through all files recursively in template directory
    for dirpath, _dirnames, filenames in os.walk(template_dir):
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
    
    # TODO: FEATURE: Option passing to sphinx-build.py
    
    cmd1 = ["python", sphinx_build, ".", "../html"]
    log.info("Sphinx build, inside directory %s" % os.getcwd())
    log.info("Running sphinx-build: %s" % subprocess.list2cmdline(cmd1))
    
    if not dry_run:
        subprocess.call(cmd1)
    
    os.chdir(old_dir)

parser = optparse.OptionParser("""sphinkydoc.py <MODULE>, ...""", 
                               description=DESCRIPTION)
"""Main parser.

This is defined in module level so that other scripts can access it.
"""

# TODO: Debug True, Prod False
parser.add_option("-v", "--verbose",
                  dest="verbose", action="store_true", default=True) 
parser.add_option("-n", "--dry-run",
                  help="don't do anything harmful, uses verbose also",
                  dest="dry_run", action="store_true", default=False)
parser.add_option("-o", "--output-dir",
                  help="outputs the html and temp directory to this "
                       "directory",
                  dest="output", default=os.getcwd())
parser.add_option("-b", "--sphinx-build-py",
                  help="path to the sphinx-build.py script",
                  dest="sphinx_build", default="sphinx-build.py")
parser.add_option("-p", "--python-path",
                  help="append this directory to python path",
                  dest="python_path", action="append", default=[], 
                  metavar='PATH')
parser.add_option("-t", "--sphinx-template-dir",
                  help="sphinx configuration template directory",
                  dest="sphinxtemplate_dir", default=DYNAMIC_SPHINX_DIR)
parser.add_option("-s", "--script",
                  dest="scripts", action="append", default=[], 
                  metavar='SCRIPT')
parser.add_option("", "--no-validation",
                  dest="validate", action="store_false", default=True)
parser.add_option("", "--caps-dir",
                  dest="caps_dir", default="../")
parser.add_option("-l", "--caps-literal",
                  help="caps files which are included as literal files, "
                       "defaults to COPYING, COPYING.LESSER, COPYING.LIB.",
                  metavar="CAPS_FILE",
                  dest="caps_literals", action="append", 
                  default=['COPYING', 'COPYING.LESSER', 'COPYING.LIB'])
    
if __name__ == '__main__':
    try:
        (options, modules) = parser.parse_args()
    except ValueError:
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
    sphinxtemplate_dir = options.sphinxtemplate_dir
    
    log.info("Creating documentation to directory '%s' ..." % options.output)
    
    # Temp directory inside the docs
    temp_dir = os.path.join(options.output, TEMP_CONFIGURATION_DIR)
    caps_dir = os.path.realpath(options.caps_dir)
    docs_dir = options.output
    
    # Remove old temp directory
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
    
    # Copy the template directory to temp directory
    copy_tree(sphinxtemplate_dir, temp_dir, dry_run=options.dry_run)
    
    # Copy all files from docs dir to temp dir, except html and temp 
    # directories.
    #copy_tree(docs_dir, temp_dir, skip_dirs=['html', '_temp'])
    
    # Generate caps files
    #caps_files = generate_caps(caps_dir, temp_dir, 
    #                             caps_literals=options.caps_literals,
    #                             dry_run=options.dry_run)
        
    # Template the temp directory
    template_dir(temp_dir, 
        file_substs={
            'conf.py' : {
                'project' : sphinx_project,
                'copyright' : sphinx_copyright,
                'version' : sphinx_version,
                'release' : sphinx_release,
            }
        }, 
        substs={
            'caps_dir' : os.path.realpath(caps_dir),
            'docs_dir' : os.path.realpath(docs_dir),
            'scripts' : [os.path.realpath(s) for s in options.scripts],
            'modules' : modules,
        }, 
        dry_run=options.dry_run)
    
    # Validates the conf.py
    if options.validate:
        log.info("Validating sphinx configuration file (using execfile)...")
        conf_file = os.path.join(temp_dir, CONFIG_FILENAME)
        
        # Ignore the Exception catch
        # pylint: disable-msg=W0703
        try:
            execfile(conf_file)
        except Exception, e:
            log.exception("Unable to validate Sphinx configuration file: %s" % e)
            sys.exit(0)
        # pylint: enable-msg=W0703
    
    run_sphinx_build(temp_dir, sphinx_build=options.sphinx_build)