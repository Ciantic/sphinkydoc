"""Sphinkydoc doc generation."""

from sphinkydocext.templating import get_module_members, get_submodules
from sphinx.ext.autosummary import import_by_name
from subprocess import Popen, PIPE
import os

__all__ = ['all_doc', 'recursive_module_doc', 'module_doc', 'script_doc', 
           'GenerateDocError']


def all_doc(tenv, module_names=None, script_paths=None):
    """Generates documentation for modules and scripts given.
    
    :param tenv: Templating environment, retrieved e.g. by 
        :func:`sphinkydocext.templating.templating_environment`.
    
    :param module_names: Root module names, documentation is generated 
        recursively for all the submodules to current working directory.
        
    :param script_paths: List of paths to scripts, generates documentation 
    files to current working directory. 
    
    """
    module_names = module_names or []
    script_paths = script_paths or []
    
    for m in module_names:
        try:
            recursive_module_doc(tenv, m)
        except GenerateDocError:
            pass
        
    for s in script_paths:
        try:
            script_doc(tenv, s)
        except GenerateDocError:
            pass


def recursive_module_doc(tenv, module_name):
    """Recursively generates module documentation also for all submodules,
    and subpackages.
    
    :param module_name: Module 
    
    """
    
    try:
        module, _name = import_by_name(module_name)
    except ImportError, e:
        raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
    
    try:
        module_doc(tenv, _name)
    except GenerateDocError:
        pass
    
    for submodule_name in get_submodules(module):
        recursive_module_doc(tenv, _name + "." + submodule_name)


def module_doc(tenv, module_name):
    """Generates documentation for module or package.
    
    :param module_name: Full name of the module.
     
    """
    
    try:
        module, name = import_by_name(module_name)
    except ImportError, e:
        raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
    
    members = get_module_members(module)
    template = tenv.get_template("sphinkydoc/module.rst")

    tcontext = {'module': module_name, 'fullname' : name }
    tcontext.update(members)
    
    # Write template, as "somemodule.submodule.rst"
    file_ = open("%s.rst" % name, 'w+')
    file_.write(template.render(tcontext))
    file_.close()


def script_doc(tenv, script_path):
    """Generates documentation for script.
    
    :param script_path: Path to script.
    :returns: reStructuredText tuple that can be used in tables.
     
    """
    script_name = os.path.basename(script_path)
    help = ""
    cmd = ["python", script_path, "--help"]
    
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    except os.error:
        return
    else:
        help, _stderr = p.communicate()
        
    help = help.replace("\r", "")
    
    template = tenv.get_template("sphinkydoc/script.rst")
    tcontext = {'script_path' : script_path, 'script_name' : script_name, 
                'help' : help}
    
    # Write template as "somescript.py"    
    file_ = open("%s.rst" % script_name, 'w+')
    file_.write(template.render(tcontext))
    file_.close()


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass