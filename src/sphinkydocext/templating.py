# -*- coding: utf-8 -*-
"""Sphinkydoc extension templating"""
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
import os

# Pylint-disable settings ----------------
# Todo messages:
#     pylint: disable-msg=W0511

# TODO: DEPENDENCY: Python 2.5 - iter_modules

def _caps(tenv, filepath, template_file, context=None):
    """Turns file to reStructuredText literal file."""
    context = context or {}
    caps_name = os.path.basename(os.path.splitext(filepath)[0])
    
    context.update({
        'caps_name' : caps_name, 
        'caps' :  open(filepath, 'r').read(),
    })
    
    t = tenv.get_template(template_file)
    tc = t.render(context)
    
    f = open(filepath, 'w+')
    f.write(tc)
    f.close()

        
def caps(tenv, filepath):
    """Preprocesses caps files by "sphinkydoc/caps.rst" jinja2 template.
    
    :path filepath: Path to the caps file.
    
    """
    _caps(tenv, filepath, "sphinkydoc/caps.rst")


def caps_literal(tenv, filepath, header=None):
    """Preprocesses caps files by "sphinkydoc/caps_literal.rst" jinja2 
    template.
    
    This assumes the given file is *not* in reStructuredText format and should
    be shown as literal block.
    
    :param filepath: Path to the file being mangled.
    :param header: Header for the created reStructuredText file, defaults to
        filename without extension.
    
    """
    
    if header is None:
        header = os.path.basename(os.path.splitext(filepath)[0])
    
    _caps(tenv, filepath, "sphinkydoc/caps_literal.rst", {'header' : header})

class TemplatePython(object):
    """Jinja2 Template python additions.
    
    Purpose of this class is to add extra callback functionality for Jinja2 
    environment, so that registered python files can handle those.
    
    Point is to have ``__template.py`` in the template directory root, which
    then is added using :meth:`TemplatePython.add` to the environment, and after
    that the ``__template.py`` can register extra functionality such as filters
    and functions to Jinja2 environment.
     
    """
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
    
    # Ignore protected member access
    # pylint: disable-msg=W0212
    #
    # Add all __template.pys
    for tdir in template_dirs_:
        tp = os.path.realpath(os.path.join(tdir, "__template.py"))
        tenv.__tp.add(tp)
    
    tenv.__tp.pre_template()
    # pylint: enable-msg=W0212
        
    return tenv
