"""Sphinkydoc document file generation."""

from sphinkydocext.templating import caps_literal, caps
from sphinkydocext.utils import multi_matcher, get_submodules, \
    get_module_members
from sphinx.ext.autosummary import import_by_name
import os
import re
import shutil
import subprocess

# TODO: Consistent returning values for the following doc generations.

def index_doc(tenv, tcontext, output_dir=None):
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
    
    f = open(filename, "w+")
    f.write(rendition)
    f.close()
    
    return filename


def included_doc(tenv, docname, src_dir, ext="rst"):
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
    shutil.move(src, dst)
    return dst
    

def all_doc(tenv, module_names=None, script_paths=None, output_dir=None):
    """Generates documentation for modules and scripts to current working 
    directory.
    
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
    
    for m in module_names:
        try:
            recursive_module_doc(tenv, m, output_dir=output_dir)
        except GenerateDocError:
            pass
        
    for s in script_paths:
        try:
            script_doc(tenv, s, output_dir=output_dir)
        except GenerateDocError:
            pass


def recursive_module_doc(tenv, module_name, output_dir=None):
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
    
    try:
        module_doc(tenv, _name)
    except GenerateDocError:
        pass
    
    for submodule_name in get_submodules(module):
        recursive_module_doc(tenv, _name + "." + submodule_name, 
                             output_dir=output_dir)


def module_doc(tenv, module_name, output_dir=None):
    """Generates documentation for module or package to current working 
    directory.
    
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
    file_ = open(filename, 'w+')
    file_.write(template.render(tcontext))
    file_.close()


def script_doc(tenv, script_path, output_dir=None):
    """Generates documentation file for script to current working directory.
    
    :param tenv: Jinja2 templating environment.
    :param script_path: Path to script.
    :param output_dir: Output directory of generated documents.
     
    """
    output_dir = output_dir or os.path.abspath(".")
    
    # TODO: Create more robust script --help parser, that can handle rST.
    
    script_name = os.path.basename(script_path)
    help = "" 
    cmd = ["python", script_path, "--help"]
    
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    except os.error:
        return
    else:
        help, _stderr = p.communicate()
        
    help = help.replace("\r", "")
    
    template = tenv.get_template("sphinkydoc/script.rst")
    tcontext = {'script_path' : script_path, 'script_name' : script_name, 
                'help' : help}

    filename = os.path.join(output_dir, "%s.rst" % script_name)

    # Write template as "somescript.py"    
    file_ = open(filename, 'w+')
    file_.write(template.render(tcontext))
    file_.close()


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
            
            caps_files.append(new_filename_wo_ext)
    
    return caps_files


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass
