
# -*- coding: utf-8 -*-

"""Sphinkydoc extension templating"""
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from pkgutil import iter_modules # TODO: DEPENDENCY: Python 2.5
import os
import inspect

__all__ = ['TemplatePython', 'templating_environment', 'get_submodules',
           'get_module_members']


class TemplatePython(object):
    """Jinja2 Template python additions."""
    def __init__(self, template_env):
        """Create templating environment wrapper.
        
        :param template_env: Templating environment, 
            :obj:`jinja2.environment.Environment`.

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
        """Adds python file to registry.
        
        :param file_: Path to the python file containing environment additions.
        
        """
        if os.path.exists(file_):
            __template = {}
            execfile(file_, __template)
            self._pythons.append((file_, __template))


def templating_environment(template_dirs=None):
    """Jinja2 templating environment.
    
    :returns: :obj:`jinja2.environment.Environment`, which is monkey patched to
        include :class:`TemplatePython` object in variable ``__tp``.
    
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


def _all_filterer(module, use_all=True):
    """All filterer for module."""
    # Explicitely defined public members
    if use_all and hasattr(module, "__all__"):
        has_all = True
        custom_all = lambda m,n: n in module.__all__
    else:
        has_all = False
        custom_all = lambda m,n: not n.startswith("_")
    return has_all, custom_all


def get_submodules(module, use_all=True, custom_all=None):
    """Get submodules of module.
    
    Uses all if required.
    
    .. note:: This is generator.
    
    """
    if custom_all is None:
        _has_all, custom_all = _all_filterer(module, use_all=use_all)
        
    # Retrieve all submodules
    if hasattr(module, "__path__"): 
        for _imp, modname, _isp in iter_modules(module.__path__):
            if custom_all(module, modname):
                yield modname
    
    
def get_module_members(module, use_all=True, custom_all=None):
    """Return module members.
    
    Crawls the module for members.
    
    """
    
    if custom_all is None:
        has_all, custom_all = _all_filterer(module, use_all=use_all)
    
    all_submodules = list(get_submodules(module))
    modules = all_submodules
    
    all_classes = []
    all_functions = []
    all_datas = []
    all_members = []
    
    for name in dir(module):
        obj = getattr(module, name)
        
        # Filter out the members that are not defined in this module, except
        # those that are listed in __all__ if any.
        if hasattr(obj, "__module__"):
            if not (has_all and custom_all(module, name)) and \
                obj.__module__ != module.__name__:
                continue
        
        if inspect.isclass(obj):
            all_classes.append(name)
        elif inspect.isfunction(obj):
            all_functions.append(name)
        elif inspect.ismodule(obj):
            continue # Not added as member either!
        else:
            all_datas.append(name)
            
        all_members.append(name)
        
    functions = [x for x in all_functions if custom_all(module, x)]
    classes = [x for x in all_classes if custom_all(module, x)]
    datas = [x for x in all_datas if custom_all(module, x)]
    members = [x for x in all_members if custom_all(module, x)]
            
    return {'all_modules': all_submodules, 'modules' : modules,
            'all_classes' : all_classes, 'classes' : classes,
            'all_functions' : all_functions, 'functions' : functions,
            'all_datas' : all_datas, 'datas' : datas,
            'all_members' : all_members, 'members' : members,}

