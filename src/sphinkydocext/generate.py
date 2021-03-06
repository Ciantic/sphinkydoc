"""Sphinkydoc document file generation.

.. note:: None of the generated documents overwrite existing documents this is to ensure 
    that your documents does not get lost.

"""

from sphinkydocext import log
from sphinkydocext.templating import caps_literal, caps
from sphinkydocext.utils import multi_matcher, get_submodules, \
    get_module_members, script_get_optparser, is_python_script, import_by_name
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
    :returns: Generated document path.
        
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
        log.info("Index generated %s file." % filename)
    
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
    :returns: Generated document path.
    
    """
    output_dir = output_dir or os.path.abspath(".")
    
    t = tenv.get_template("sphinkydoc/README.html")
    rendition = t.render({'docs_url' : docs_url })
    
    filename = os.path.join(output_dir, "README.html")
        
    if overwrite or not os.path.exists(filename):
        f = open(filename, "w+")
        f.write(rendition)
        f.close()
        log.info("README.html generated %s file." % filename)
        
    return filename


def included_doc(tenv, docname, src_dir, ext="rst", overwrite=False):
    """Included documents pre-processed.
    
    Sphinx does not allow included documents to be with same prefix as the 
    normal documents, so we have to rename them so Sphinx won't throw warnings.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    :param docname: Name of the included doc, without extension.
    :param src_dir: Source directory where to look for.
    :param ext: Extension of source files, defaults to ".rst".
    :returns: Generated document path.
    
    """
    src = os.path.join(src_dir, "%s.%s" % (docname, ext))
    dst = os.path.join(src_dir, "%s.%s" % (docname, "inc"))
    if overwrite or not os.path.exists(dst):
        shutil.move(src, dst)
        log.info("Included %s, moved to %s" % (src, dst))
    return dst


def conf_py(tenv, tcontext, output_dir=None, overwrite=False):
    """Generates sphinx conf.py, cannot be used within extension.
    
    :param tenv: Jinja2 templating environment.
    :param output_dir: Output directory of generated documents.
    :returns: Generated document path.
     
    """
    template = tenv.get_template("sphinkydoc/conf.py.template")
    
    rendition = template.render(tcontext)
    filename = os.path.join(output_dir, "conf.py")
    
    if overwrite or not os.path.exists(filename):
        f = open(filename, "w+")
        f.write(rendition)
        f.close()
        log.info("Conf generated %s file." % filename)
        
    return filename


def all_doc(tenv, module_names=None, script_paths=None, module_output_dir="",
            script_output_dir="", module_overwrite=False, 
            script_overwrite=False, source_dir=""):
    """Generates documentation for modules and scripts.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    
    :param module_names: Root module names, documentation is generated 
        recursively for all the submodules.
        
    :param script_paths: List of paths to scripts, creates documentation files 
        for these. 
    
    :param module_output_dir: Output directory of generated module documents.
        **Must be relative path to source root.**
        
    :param script_output_dir: Output directory of generated script documents.
        **Must be relative path to source root.**
        
    :param source_dir: Source directory, preferably absolute path.
    
    :returns: Tuple of generated module paths, and generated script paths.
    
    """
    
    module_names = module_names or []
    script_paths = script_paths or []
    
    module_files = []
    script_files = []
    
    for m in module_names:
        try:
            module_files.extend(recursive_module_doc(tenv, m, 
                                                     output_dir=module_output_dir,
                                                     source_dir=source_dir, 
                                                     overwrite=module_overwrite))
        except GenerateDocError, er:
            log.warning("Unable to generating module doc for '%s':  %s", 
                        m, unicode(er))
        
    for s in script_paths:
        try:
            script_files.append(script_doc(tenv, s, output_dir=script_output_dir,
                                           source_dir=source_dir, 
                                           overwrite=script_overwrite))
        except GenerateDocError, er:
            log.warning("Unable to generating script doc for '%s':  %s", 
                        s, unicode(er))
    
    return module_files, script_files


def recursive_module_doc(tenv, module_name, output_dir="", source_dir="", 
                         overwrite=False):
    """Recursively generates module documentation also for all submodules,
    and subpackages.
    
    :param tenv: Jinja2 templating environment. :param module_name: Module
    :param source_dir: Source directory.
    :param output_dir: Output directory of generated documents. **Must be
        relative to the source directory!** :returns: List of generated document
        paths.
    
    """
    
    module_files = []
    
    # We must try to import the module, so we can recurse to the submodules
    try:
        module, _name = import_by_name(module_name)
    except ImportError:
        log.warning("Unable to import '%s', docs for this module cannot "
                    "be generated.", module_name)
    else:
        
        # Try to generate documentation for this module 
        try:
            module_files.append(\
                module_doc(tenv, module_name, output_dir=output_dir, 
                           source_dir=source_dir, overwrite=overwrite))
        except GenerateDocError, er:
            log.warning("Unable to generate module doc for '%s':  %s", 
                        module_name, unicode(er))
    
        # Continue to found submodules
        for submodule_name in get_submodules(module):
            module_files.extend(\
                recursive_module_doc(tenv, _name + "." + submodule_name, 
                                     output_dir=output_dir, 
                                     source_dir=source_dir,
                                     overwrite=overwrite))
    
    return module_files


def module_doc(tenv, module_name, output_dir="", source_dir="", 
               overwrite=False):
    """Generates documentation for module or package.
    
    :param tenv: Jinja2 templating environment.
    :param module_name: Full name of the module.
    :param source_dir: Source directory.
    :param output_dir: Output directory of generated documents, 
        **must be relative to the source directory!**
    :returns: Generated document path.
     
    """
    
    try:
        module, name = import_by_name(module_name)
    except ImportError, e:
        raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
    
    members = get_module_members(module)
    template = tenv.get_template("sphinkydoc/module.rst")

    tcontext = {'module': module_name, 
                'output_dir' : output_dir, 
                'fullname' : name }
    tcontext.update(members)
    filename = os.path.join(source_dir, output_dir, "%s.rst" % name)
    
    # Write template, as "somemodule.submodule.rst"
    if overwrite or not os.path.exists(filename):
        file_ = open(filename, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        log.info("Module generated %s file." % filename)
        
    return filename


def script_doc_py(tenv, script_path, optparser, output_dir="",
                  source_dir="", overwrite=False):
    """Generates documentation file for script using :mod:`optparser`.
    
    :param tenv: Jinja2 templating environment.
    :param optparser: :obj:`optparse.OptionParser`
    :param script_path: Path to script.
    :param source_dir: Source directory.
    :param output_dir: Output directory of generated documents, 
        **must be relative to the source directory!**
    :returns: Generated document path.
     
    """
    
    
    script_name = os.path.basename(script_path)
    
    filename = os.path.join(source_dir, output_dir, "%s.rst" % script_name)
    filename_t = os.path.join(source_dir, output_dir, 
                              "%s.rst.template" % script_name)
    
    if os.path.exists(filename_t):
        template = tenv.from_string(open(filename_t).read())
    else:    
        template = tenv.get_template("sphinkydoc/script_python.rst")
        
    tcontext = {'script_path' : script_path, 
                'output_dir' : output_dir,
                'script_name' : script_name, 
                'optparser' : optparser}

    # Write template as "somescript.py"    
    if overwrite or not os.path.exists(filename):
        file_ = open(filename, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        log.info("Script generated %s file." % filename)
        
    return filename


def script_doc_help(tenv, script_path, output_dir=None, source_dir="", 
                    overwrite=False):
    """Generates documentation file for script using ``--help``.
    
    :param tenv: Jinja2 templating environment.
    :param script_path: Path to script.
    :param source_dir: Source directory.
    :param output_dir: Output directory of generated documents.
    :returns: Generated document path.
     
    """
    output_dir = output_dir or os.path.abspath(".")
    
    script_name = os.path.basename(script_path)
    help_text = ""
    
    # Call the script using "--help"
    cmd = ["python", script_path, "--help"]
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    except os.error:
        return
    else:
        help_text, _stderr = p.communicate()
        
    help_text = help_text.replace("\r", "")
    filename = os.path.join(source_dir, output_dir, "%s.rst" % script_name)
    filename_t = os.path.join(source_dir, output_dir, 
                              "%s.rst.template" % script_name)
    
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
        log.info("Script generated %s file." % filename)
        
    return filename


def script_doc(tenv, script_path, output_dir=None, source_dir=None, 
               overwrite=False):
    """Generates documentation file for script.
    
    :param tenv: Jinja2 templating environment.
    :param script_path: Path to script.
    :param source_dir: Source directory.
    :param output_dir: Output directory of generated documents.
    :returns: Generated document path.
     
    """
    
    # First tries to get optparser for python scripts
    if is_python_script(script_path):
        optparser = script_get_optparser(script_path)
        if optparser:
            return script_doc_py(tenv, script_path, optparser, 
                                 source_dir=source_dir, output_dir=output_dir, 
                                 overwrite=overwrite)
    
    # Fallback to --help
    return script_doc_help(tenv, script_path, output_dir=output_dir, 
                           source_dir=source_dir, overwrite=overwrite)


def caps_doc(tenv, caps_dir, ext='rst', caps_literals=None, output_dir=None, 
             dry_run=False, overwrite=False, 
             allowed_exts=['rst', 'inc', 'txt', '']):
    """Generate documentation from caps files in ``caps_dir``.
    
    Caps files are files such as INSTALL, COPYING, README, which contain 
    documentation worthy content outside docs directory.
    
    :param caps_dir: Directory where caps files reside.
    :param dst_dir: Destination directory where caps files are *copied*.
    :param ext: Enforce all caps files to be in this extension.
    :param caps_literals: Caps files that are treated as literal files.
    :param output_dir: Output directory of generated documents.
    :param dry_run: Dry run only, no copying or other harmful changes.
    :param overwrite: Overwrite the existing file? Defaults to :const:`False`.
    :param allowed_ext: List of allowed extensions.
    
    :returns: List of generated document paths. 
    
    """
    caps_literals = caps_literals or []
    caps_files = []
    
    dir_contents = os.listdir(caps_dir)
    output_dir = output_dir or os.path.abspath(".")
    
    caps_matcher = multi_matcher(caps_literals)
    
    for filename in dir_contents:
        if re.match(r"^[A-Z]{3,}(\.[A-Za-z]+)?$", filename):
            
            # Gather information about the file
            _root, _ext = os.path.splitext(filename)
            f_base = os.path.basename(_root)
            f_ext = _ext.lower()[1:]
            
            # If not allowed extension, skip
            if not any(f_ext == allowed_ext for allowed_ext in allowed_exts):
                continue
            
            output_filename = f_base + "." + ext
            
            filepath = os.path.join(caps_dir, filename)
            output_filepath = os.path.join(output_dir, output_filename)
            
            if not dry_run:
                if overwrite or not os.path.exists(output_filepath):
                    shutil.copy(filepath, output_filepath)
                    log.info("Caps %s copied to %s" % (filepath, output_filepath))
                    
            if caps_matcher(f_base):        
                caps_literal(tenv, output_filepath)
            else:
                caps(tenv, output_filepath)
            
            caps_files.append(output_filepath)
    
    return caps_files


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass
