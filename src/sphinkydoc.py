"""SphinkyDoc script"""
from string import Template
import subprocess
import shutil
import logging
import optparse
import sys
import sphinkydocext
import os
import re

logging.basicConfig()
log = logging.getLogger("sphinkydoc")

DYNAMIC_SPHINX_DIR = 'data'
CONFIG_FILENAME = 'conf.py'
TEMP_CONFIGURATION_DIR = '_temp'

def copy_data(src_dir, dst_dir, remove_dst=True, dry_run=False):
    """Copies data between two directories.
    
    .. note:: Removes the dst_dir by default!
    
    """
    if not dry_run:
        if os.path.exists(dst_dir) and remove_dst:
            log.info("Deleting the old dst directory '%s'..." % dst_dir)
            try:
                shutil.rmtree(dst_dir)
            except:
                log.exception("Cannot delete old dst directory '%s'..." % dst_dir)
                sys.exit(0)
            
        log.info("Copying the data '%s' to dst '%s' ..." % (src_dir, dst_dir))
        try:
            shutil.copytree(src_dir, dst_dir)
        except:
            log.exception("Cannot copy the data dir '%s' to temp dir '%s'." \
                          % (src_dir, dst_dir))    
            sys.exit(0)
        
def template_dir(template_dir, file_substs=None, substs=None, dry_run=False):
    """Templates the directory.
    
    All files inside template_dir which has ".template" in filename is templated
    using :class:`string.Template`.
    
    :param template_dir: Path to directory of templating.
    :param file_substs: Dictionary of template substitions by filename relative 
        to templating directory
    :param substs: Base substitions for *all* templates.
    :param dry_run: Dry run, no harmful changes done.
    
    """
    log.info("Templating the directory: %s" % template_dir)
    substs = substs or {}
    file_substs = file_substs or {}
    
    template_abs_path = os.path.realpath(template_dir)
    
    def valid_template_filename(filename):
        return ".template" in filename and len(filename) > len(".template")
    
    for dirpath, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            
            # Is valid template
            if not valid_template_filename(filename):
                continue
            
            # Template file path destination
            filepath_dst = os.path.join(dirpath, 
                                      filename.replace(".template", ""))
            
            log.info("Moving '%s' to '%s' ..." % (filepath, filepath_dst))
            
            # Move template to destination
            if not dry_run:
                shutil.move(filepath, filepath_dst)
                filepath = filepath_dst
                
            rel_filepath = filepath[len(template_abs_path)+1:].replace("\\", 
                                                                     "/")
            
            # Read the file to template object
            try:
                log.info("Reading template file '%s' ..." % rel_filepath)
                f = open(filepath, 'r')
                t = Template(f.read())
                f.close()
            except:
                log.exception("Dynamic config template '%s' is not readable." % \
                              rel_filepath)
                sys.exit(0)
            
            # Get template substitions
            s = {}
            s.update(substs)
            s.update(file_substs.get(rel_filepath, {}))
            
            # Try to template using substition
            try:
                tmp = t.substitute(s)
            except KeyError, er:
                log.error("Template '%s' is missing value for key: %s" % (rel_filepath, er))
            else:
                log.info("Writing the templated substition to '%s'..." % rel_filepath)
                
                try:
                    if not dry_run:
                        f = open(filepath, 'w+')
                        f.write(tmp)
                        f.close()
                except:
                    log.exception("Template file '%s' is not writable..." % filepath)
                    sys.exit(0)
    log.info("Directory templated.")
                    
def run_sphinx_build(sphinx_conf_dir, dry_run=False, sphinx_build='sphinx-build.py'):
    """Runs the sphinx-build.py in given directory."""
    cmd = ["python", sphinx_build, "-b", "html", "-d", "_temp/_build/doctrees", "_temp/", "html"]
    log.info("Sphinx build, inside directory %s" % os.getcwd())
    log.info("Running sphinx-build: %s" % subprocess.list2cmdline(cmd))
    
    if not dry_run:
        subprocess.call(cmd)

if __name__ == '__main__':
    parser = optparse.OptionParser("""sphinkydoc.py <PACKAGE/MODULE NAME>""")
    
    parser.add_option("-v", "--verbose",
                      dest="verbose", action="store_true", default=True) # TODO: Debug True, Prod False
    parser.add_option("-n", "--dry-run", 
                      dest="dry_run", action="store_true", default=False)
    parser.add_option("-o", "--output-dir",
                      dest="output", default=os.getcwd())
    parser.add_option("-b", "--sphinx-build-py",
                      dest="sphinx_build", default="sphinx-build.py")
    parser.add_option("-s", "--sphinx-template-dir",
                      dest="sphinxtemplate_dir", default='')
    parser.add_option("", "--no-validation",
                      dest="validate", action="store_false", default=True)
    try:
        (options, (module_name, )) = parser.parse_args()
    except:
        parser.print_usage()
        sys.exit(0)
        
    # Be verbose if on dry run
    if options.verbose or options.dry_run:
        log.setLevel(logging.INFO)
    
    # Sphinx configuration template directory 
    sphinxtemplate_dir = options.sphinxtemplate_dir
    if not sphinxtemplate_dir:
        sphinxtemplate_dir = os.path.join(os.path.dirname(sphinkydocext.__file__),
                                          DYNAMIC_SPHINX_DIR)
    
    log.info("Creating documentation for '%(package)s' to "
             "directory '%(dir)s' ..." % {'package': module_name, 
                                        'dir': options.output })
    
    # Temp directory inside the docs
    temp_dir = os.path.join(options.output, TEMP_CONFIGURATION_DIR)
    
    # Copy the template directory to temp directory
    copy_data(sphinxtemplate_dir, temp_dir, remove_dst=True, 
              dry_run=options.dry_run)
    
    # Template the temp directory
    template_dir(temp_dir, file_substs={
            'conf.py' : {
                'project' : '%s.__project__' % module_name,
                'copyright' : '%s.__copyright__' % module_name,
                'version' : '%s.__version__' % module_name,
                'release' : '%s.__release__' % module_name,
            }
        }, 
        substs={
            'yourmodule' : module_name,
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