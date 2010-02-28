"""Sphinkydoc document file generation."""

from optparse import OptionParser
from sphinkydocext import log
from sphinkydocext.templating import caps_literal, caps
from sphinkydocext.utils import multi_matcher, get_submodules, \
    get_module_members
from sphinx.ext.autosummary import import_by_name
import os
import re
import shutil
import subprocess

# TODO: Consistent returning values for the following doc generations.

def index_doc(tenv, tcontext, output_dir=None, overwrite=False):
    """Generate documentation index.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    :param output_dir: Output directory of generated document.
        
    """
    
    output_dir = output_dir or os.path.abspath(".")
    t = tenv.get_template("sphinkydoc/index.rst")
    rendition = t.render(tcontext)
    
    master = "index"
    suffix = "rst"
    filename = os.path.join(output_dir, "%s.%s" % (master, suffix))
    
    if overwrite or not os.path.exists(filename):
        f = open(filename, "w+")
        f.write(rendition)
        f.close()
    
    return filename


def readme_html_doc(tenv, docs_url, output_dir=None, overwrite=False):
    """Create README.html shortcut.
    
    Purpose is to have README.html that points to "docs/html/index.html" if it
    exists. If it does not exist, the distribution is most likely fetched from
    version control where HTML documentation is not generated, in this case the
    link should point to homepage which has always the versioned documentation.
    
    This way we can provide both, the end users of the project and users of 
    version control the easiest way to access the documentation.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    
    :param output_dir: Output directory of generated document.
    
    """
    output_dir = output_dir or os.path.abspath(".")
    
    t = tenv.get_template("sphinkydoc/README.html")
    rendition = t.render({'docs_url' : docs_url })
    
    filename = os.path.join(output_dir, "README.html")
        
    if overwrite or not os.path.exists(filename):
        f = open(filename, "w+")
        f.write(rendition)
        f.close()

def included_doc(tenv, docname, src_dir, ext="rst", overwrite=False):
    """Included documents pre-processed.
    
    Sphinx does not allow included documents to be with same prefix as the 
    normal documents, so we have to rename them so Sphinx won't throw warnings.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    :param docname: Name of the included doc, without extension.
    :param src_dir: Source directory where to look for.
    :param ext: Extension of source files, defaults to ".rst".
    
    """
    src = os.path.join(src_dir, "%s.%s" % (docname, ext))
    dst = os.path.join(src_dir, "%s.%s" % (docname, "inc"))
    if overwrite or not os.path.exists(dst):
        shutil.move(src, dst)
    return dst
    

def all_doc(tenv, module_names=None, script_paths=None, output_dir=None, 
            overwrite=False):
    """Generates documentation for modules and scripts.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    
    :param module_names: Root module names, documentation is generated 
        recursively for all the submodules.
        
    :param script_paths: List of paths to scripts, creates documentation files 
        for these. 
    
    :param output_dir: Output directory of generated document.
    
    """
    output_dir = output_dir or os.path.abspath(".")
    
    module_names = module_names or []
    script_paths = script_paths or []
    
    module_files = []
    script_files = []
    
    for m in module_names:
        try:
            module_files.extend(recursive_module_doc(tenv, m, 
                                                     output_dir=output_dir, 
                                                     overwrite=overwrite))
        except GenerateDocError:
            pass
        
    for s in script_paths:
        try:
            script_files.append(script_doc(tenv, s, output_dir=output_dir, 
                                           overwrite=overwrite))
        except GenerateDocError:
            pass
    
    return module_files, script_files

def recursive_module_doc(tenv, module_name, output_dir=None, overwrite=False):
    """Recursively generates module documentation also for all submodules,
    and subpackages.
    
    :param tenv: Jinja2 templating environment.
    :param module_name: Module 
    :param output_dir: Output directory of generated documents.
    
    """
    output_dir = output_dir or os.path.abspath(".")
    
    try:
        module, _name = import_by_name(module_name)
    except ImportError, e:
        raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
    
    module_files = []
    
    try:
        module_files.append(module_doc(tenv, _name, output_dir=output_dir, 
                                       overwrite=overwrite))
    except GenerateDocError:
        pass
    
    for submodule_name in get_submodules(module):
        module_files.extend(recursive_module_doc(tenv, 
                                                 _name + "." + submodule_name, 
                                                 output_dir=output_dir))
    
    return module_files

def module_doc(tenv, module_name, output_dir=None, overwrite=False):
    """Generates documentation for module or package.
    
    :param tenv: Jinja2 templating environment.
    :param module_name: Full name of the module.
    :param output_dir: Output directory of generated documents.
    
     
    """
    output_dir = output_dir or os.path.abspath(".")
    
    try:
        module, name = import_by_name(module_name)
    except ImportError, e:
        raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
    
    members = get_module_members(module)
    template = tenv.get_template("sphinkydoc/module.rst")

    tcontext = {'module': module_name, 'fullname' : name }
    tcontext.update(members)
    filename = os.path.join(output_dir, "%s.rst" % name)
    
    # Write template, as "somemodule.submodule.rst"
    if overwrite or not os.path.exists(filename):
        file_ = open(filename, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        
    return filename


def script_get_optparser(script_path):
    """Gets optparser from script, if possible.
    
    Idea is to loop all globals after :func:`execfile` and look for
    :obj:`optparser.OptionParser` instances.
    
    :param script_path: Path to the script.
    :returns: :const:`None`, or :obj:`optparse.OptionParser`
    
    """
    globs = {}
    log.info("Python execfile script: %s" % script_path)
    
    execfile(script_path, globs)
    for _n, val in globs.iteritems():
        # TODO: LOW: We could probably do more duck-typing friendly check here
        # too, but that is low priority.
        if isinstance(val, OptionParser):
            log.info("Found OptionParser.")
            return val


def script_doc_py(tenv, script_path, optparser, output_dir=None, 
                  overwrite=False):
    """Generates documentation file for script using :mod:`optparser`.
    
    :param tenv: Jinja2 templating environment.
    :param optparser: :obj:`optparse.OptionParser`
    :param script_path: Path to script.
    :param output_dir: Output directory of generated documents.
     
    """
    output_dir = output_dir or os.path.abspath(".")
    
    script_name = os.path.basename(script_path)
    
    filename = os.path.join(output_dir, "%s.rst" % script_name)
    filename_t = os.path.join(output_dir, "%s.rst.template" % script_name)
    
    if os.path.exists(filename_t):
        template = tenv.from_string(open(filename_t).read())
    else:    
        template = tenv.get_template("sphinkydoc/script_python.rst")
        
    tcontext = {'script_path' : script_path, 
                'script_name' : script_name, 
                'optparser' : optparser}

    # Write template as "somescript.py"    
    if overwrite or not os.path.exists(filename):
        file_ = open(filename, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        
    return filename


def script_doc_help(tenv, script_path, output_dir=None, overwrite=False):
    """Generates documentation file for script using ``--help``.
    
    :param tenv: Jinja2 templating environment.
    :param script_path: Path to script.
    :param output_dir: Output directory of generated documents.
     
    """
    output_dir = output_dir or os.path.abspath(".")
    
    script_name = os.path.basename(script_path)
    help_text = ""
    
    cmd = ["python", script_path, "--help"]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    except os.error:
        return
    else:
        help_text, _stderr = p.communicate()
        
    help_text = help_text.replace("\r", "")
    filename = os.path.join(output_dir, "%s.rst" % script_name)
    filename_t = os.path.join(output_dir, "%s.rst.template" % script_name)
    
    if os.path.exists(filename_t):
        template = tenv.from_string(open(filename_t).read())
    else:    
        template = tenv.get_template("sphinkydoc/script.rst")
        
    tcontext = {'script_path' : script_path, 
                'script_name' : script_name, 
                'help' : help_text}

    # Write template as "somescript.py"    
    if overwrite or not os.path.exists(filename):
        file_ = open(filename, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        
    return filename


def script_doc(tenv, script_path, output_dir=None, overwrite=False):
    """Generates documentation file for script.
    
    :param tenv: Jinja2 templating environment.
    :param script_path: Path to script.
    :param output_dir: Output directory of generated documents.
     
    """
    
    # First try to get the optparser
    optparser = script_get_optparser(script_path)
    if optparser:
        return script_doc_py(tenv, script_path, optparser, 
                             output_dir=output_dir, overwrite=overwrite)
    
    # Fallback to --help
    return script_doc_help(tenv, script_path, output_dir=output_dir, 
                          overwrite=overwrite)


def caps_doc(tenv, caps_dir, ext='rst', caps_literals=None, output_dir=None, 
             dry_run=False):
    """Generate documentation from caps files in ``caps_dir``.
    
    Caps files are files such as INSTALL, COPYING, README, which contain 
    documentation worthy content outside docs directory.
    
    :param caps_dir: Directory where caps files reside.
    :param dst_dir: Destination directory where caps files are *copied*.
    :param ext: Enforce all caps files to be in this extension.
    :param caps_literals: Caps files that are treated as literal files.
    :param output_dir: Output directory of generated documents.
    :param dry_run: Dry run only, no copying or other harmful changes.
    
    :returns: List of caps files docced without extension. 
    
    """
    caps_literals = caps_literals or []
    caps_files = []
    
    dir_contents = os.listdir(caps_dir)
    output_dir = output_dir or os.path.abspath(".")
    
    caps_matcher = multi_matcher(caps_literals)
    
    for filename in dir_contents:
        if re.match("^[A-Z](\.[A-Za-z]+)?", filename):
            new_filename = filename
            
            # Add the extension if not there
            if not filename.endswith(ext):
                new_filename += '.%s' % ext
                
            new_filename_wo_ext = new_filename[:-len(ext)-1]

            filepath = os.path.join(caps_dir, filename)
            new_filepath = os.path.join(output_dir, new_filename)
            
            if not dry_run:
                if not os.path.exists(new_filepath):
                    shutil.copy(filepath, new_filepath)
                    
            if caps_matcher(new_filename_wo_ext):        
                caps_literal(tenv, new_filepath)
            else:
                caps(tenv, new_filepath)
            
            caps_files.append(new_filepath)
    
    return caps_files


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass
