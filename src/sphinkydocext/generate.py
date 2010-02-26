import os
import sys
from sphinkydocext.templating import templating_environment, get_module_members, \
    get_submodules

from subprocess import Popen, PIPE
from sphinx.ext.autosummary import import_by_name

def all_doc(tenv, module_names, script_paths):
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
    """Iteratively generates module documentation for all submodules,
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
    
    # Create directory for module_name
    #if not os.path.exists(module_name):  
    #    os.mkdir(module_name)
    # print >> sys.stderr, "Mod name: %s, fullname: %s" % (module_name, name)
    tcontext = {'module': module_name, 'fullname' : name }
    tcontext.update(members)
    
    # Write template
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
    
    file_ = open("%s.rst" % script_name, 'w+')
    file_.write(template.render(tcontext))
    file_.close()


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass