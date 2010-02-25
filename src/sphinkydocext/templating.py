
# -*- coding: utf-8 -*-

"""Sphinkydoc extension templating"""
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from pkgutil import iter_modules # TODO: DEPENDENCY: Python 2.5
import os
import sys
import inspect

__all__ = ['TemplatePython', 'templating_environment', 'get_submodules',
           'get_module_members']

class TemplatePython(object):
    """Jinja2 Template python additions."""
    def __init__(self, template_env):
        """Create templating environment wrapper.
        
        :param template_env: Templating environment, 
            :obj:`jinja2.environment.Environment`.
            
        :param template_pythons:
        
        """
        self._template_env = template_env
        self._pythons = []
    
    def __getattr__(self, name):
        if name not in ['_template_env', '_pythons', 'add']:
            def curry_template_python(*args, **kwargs):
                
                r = []
                for tp_path, tp in self._pythons:
                    if not tp.has_key(name):
                        continue
                    
                    w = os.getcwd()
                    os.chdir(os.path.dirname(tp_path))
                    r.append((tp_path, tp[name](self._template_env, *args, **kwargs)))
                    os.chdir(w)
                
                return r
            
            return curry_template_python
        
        return super(TemplatePython, self).__getattribute__(name)
    
    def add(self, file_):
        """Adds file to TemplatePython registry.
        
        :param file_: Path to the file containing environment additions.
        
        """
        if os.path.exists(file_):
            __template = {}
            execfile(file_, __template)
            self._pythons.append((file_, __template))

def templating_environment(template_dirs=None):
    """Jinja2 templating environment.
    
    Returned environment is monkey patched to include TemplatePython object in 
    variable ``__tp``.
    
    :returns: :obj:`jinja2.environment.Environment`
    
    """
    
    template_dirs_ = [os.path.realpath(
                        os.path.join(os.path.dirname(__file__), 'templates')
                     )]
    
    if template_dirs is not None:
        template_dirs_.extend(template_dirs)
        
    template_loader = FileSystemLoader(template_dirs_)
    tenv = SandboxedEnvironment(loader=template_loader)
    
    tenv.__tp = TemplatePython(tenv) 
    
    # Add all __template.pys
    for tdir in template_dirs_:
        tp = os.path.realpath(os.path.join(tdir, "__template.py"))
        tenv.__tp.add(tp)
    
    tenv.__tp.pre_template()
        
    return tenv

def _all_filter(module, use_all=True):
    """Returns all filterer for module."""
    custom_all = lambda m, s: not s.startswith("_")
    
    if use_all:
        try:
            all_ = module.__all__
        except AttributeError:
            if use_all:
                print >> sys.stderr, ("Module %s is missing __all__, "
                                      "falling back to public members." \
                                      % module.__name__)
        else:
            custom_all = lambda m, s: s in all_
    return custom_all

def get_submodules(module, use_all=True, custom_all=None):
    """Get submodules of module.
    
    Uses all if required.
    
    .. note:: This is generator.
    
    """
    if not custom_all:
        custom_all = _all_filter(module, use_all)
        
    # Retrieve all submodules
    if hasattr(module, "__path__"): 
        for _imp, modname, _isp in iter_modules(module.__path__):
            if custom_all(module, modname):
                yield modname
    
def get_module_members(module):
    """Return module members.
    
    Crawls the module for members.
    
    """
    all_filter = _all_filter(module, use_all=True)
    
    def custom_all(n):
        return all_filter(module, n)
    
    all_submodules = list(get_submodules(module))
    modules = all_submodules
    
    all_classes = []
    all_functions = []
    all_attributes = []
    all_members = []
    
    for name in dir(module):
        obj = getattr(module, name)
        all_members.append(name)
        
        if inspect.isclass(obj):
            all_classes.append(name)
        elif inspect.isfunction(obj):
            all_functions.append(name)
        elif inspect.ismodule(obj):
            pass
        else:
            all_attributes.append(name)
            
    functions = filter(custom_all, all_functions)
    classes = filter(custom_all, all_classes)
    attributes = filter(custom_all, all_attributes)
    members = filter(custom_all, all_members)
            
    return {'all_modules': all_submodules, 'modules' : modules,
            'all_classes' : all_classes, 'classes' : classes,
            'all_functions' : all_functions, 'functions' : functions,
            'all_attributes' : all_attributes, 'attributes' : attributes,
            'all_members' : all_members, 'members' : members,}

