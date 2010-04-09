"""SphinkyDoc script"""
from sphinkydocext.directives.sphinkydoc import templating_environment
from sphinkydocext.generate import conf_py
import logging
import optparse
import os
import shutil
import subprocess
import sys

DESCRIPTION = """Sphinx automated documentation generator and builder script.
Main purpose is to generate documentation for small projects, which usually does
not require external written documents."""

parser = optparse.OptionParser("""%prog [options] primarymodule, ...""", 
                               description=DESCRIPTION)
"""Main parser.

This is defined in module level so that other scripts can access it.
"""

parser.add_option("-v", "--verbose",
                  dest="verbose", action="store_true", default=False) 
parser.add_option("-n", "--dry-run",
                  help="don't do anything harmful, uses verbose also",
                  dest="dry_run", action="store_true", default=False)
parser.add_option("-o", "--output-dir",
                  help="outputs the html and temp directory to this "
                       "directory, defaults to current working directory",
                  dest="output", default=None)
parser.add_option("-b", "--sphinx-build-py",
                  help="path to the sphinx-build.py script",
                  dest="sphinx_build", default="sphinx-build.py")
parser.add_option("-p", "--python-path",
                  help="append this directory to python path",
                  dest="python_path", action="append", default=[], 
                  metavar='PATH')
parser.add_option("-s", "--script",
                  help="path to the which to generate documentation",
                  dest="scripts", action="append", default=[], 
                  metavar='SCRIPT_PATH')
parser.add_option("", "--no-validation",
                  dest="validate", action="store_false", default=True)
parser.add_option("", "--caps-dir",
                  dest="caps_dir", default="../")
parser.add_option("-l", "--caps-literal",
                  help="caps files which are included as literal files, "
                       "defaults to COPYING.* files",
                  metavar="CAPS_FILE",
                  dest="caps_literals", action="append", 
                  default=None)
    
# Pylint-disable settings ----------------
# Todo messages:
#     pylint: disable-msg=W0511

logging.basicConfig()
log = logging.getLogger("sphinkydoc")

CONFIG_FILENAME = 'conf.py'
SPHINX_DIR = '_temp'
HTML_DIR = 'html'

def run_sphinx_build(sphinx_conf_dir, html_dir, dry_run=False,
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
    
    cmd1 = ["python", sphinx_build, ".", html_dir]
    log.info("Sphinx build, inside directory %s" % os.getcwd())
    log.info("Running sphinx-build: %s" % subprocess.list2cmdline(cmd1))
    
    if not dry_run:
        subprocess.call(cmd1)
    
    os.chdir(old_dir)

if __name__ == '__main__':
    (options, modules) = parser.parse_args()
        
    sphinx_project = '%s.__project__' % modules[0]
    sphinx_copyright = '%s.__copyright__' % modules[0]
    sphinx_version = '%s.__version__' % modules[0]
    sphinx_release = '%s.__release__' % modules[0]
    
    # Warnings only
    log.setLevel(logging.WARNING)
    
    # Be verbose if on dry run
    if options.verbose or options.dry_run:
        log.setLevel(logging.INFO)
        
    output_dir = options.output or os.getcwd()
    
    log.info("Creating %s,%s to directory '%s' ...", HTML_DIR, SPHINX_DIR, 
             output_dir)
    
    # Temp directory inside the docs
    temp_dir = os.path.join(output_dir, SPHINX_DIR)
    html_dir = os.path.join(output_dir, HTML_DIR)
    caps_dir = options.caps_dir
    caps_literals = options.caps_literals
    docs_dir = output_dir
    scripts = options.scripts
    
    # Remove old temp directory
    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
        
    if os.path.isdir(html_dir):
        shutil.rmtree(html_dir)
        
    os.mkdir(temp_dir)
        
    # Template the temp directory
    tcontext = {
        'project' : sphinx_project,
        'copyright' : sphinx_copyright,
        'version' : sphinx_version,
        'release' : sphinx_release,
        'caps_literals' : caps_literals,
        'caps_dir' : os.path.realpath(caps_dir),
        'docs_dir' : os.path.realpath(docs_dir),
        'scripts' : [os.path.realpath(s) for s in scripts],
        'modules' : modules,
    }
    
    # Generate conf_py
    conf_py(templating_environment(), tcontext, output_dir=temp_dir)
    
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
    
    run_sphinx_build(temp_dir, html_dir, sphinx_build=options.sphinx_build)
    