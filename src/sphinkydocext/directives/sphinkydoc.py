# -*- coding: utf-8 -*-

"""Sphinkydoc directive"""
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from pkgutil import iter_modules # TODO: DEPENDENCY: Python 2.5
from sphinkydocext.utils import quote_split
from sphinx import addnodes
from sphinx.ext.autosummary import import_by_name
from sphinx.util.compat import Directive
from subprocess import Popen, PIPE
import os
import sys
import inspect

__all__ = ['TemplatePython', 'templating_environment', 'get_submodules',
           'get_module_members', 'sphinkydoc_toc', 'Sphinkydoc']

class TemplatePython(object):
    def __init__(self, template_env, template_pythons=None):
        self._template_env = template_env
        self._pythons = template_pythons or []
    
    def __getattr__(self, name):
        
        if name not in ['_template_env', '_pythons']:
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
        
        return super(TemplatePython, self).__getattr__(name)

def template_python(file_):
    if os.path.exists(file_):
        __template = {}
        execfile(file_, __template)
        return __template
    return {}        

def templating_environment(template_dirs=None):
    """Jinja2 templating environment.
    
    :returns: :obj:`jinja2.environment.Environment`
    
    """
    
    template_dirs_ = [os.path.realpath(
                        os.path.join(os.path.dirname(__file__) + "/../",
                                     'templates')
                     )]
    
    if template_dirs is not None:
        template_dirs_.extend(template_dirs)
        
    template_loader = FileSystemLoader(template_dirs_)
    tenv = SandboxedEnvironment(loader=template_loader)
    
    tenv.__tp = TemplatePython(tenv) 
    
    # Add all __template.pys
    for tdir in template_dirs_:
        tp = os.path.realpath(os.path.join(tdir, "__template.py"))
        tenv.__tp._pythons.append((tp, template_python(tp)))
    
    tenv.__tp.pre_template()
        
    return tenv

def _all_filter(module, use_all=True):
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


class sphinkydoc_toc(nodes.comment):
    """Dummy toc node."""
    pass

class Sphinkydoc(Directive):
    """Sphinkydoc directive.
    
    Usage in reStructuredText::
    
        .. sphinkydoc::
            :scripts: firstscript.py secondscript.py "third script.py"
            :modules: firstmod secondmod
    
    """
    
    option_spec = {
        'no-gen': directives.unchanged, 
        'maxdepth': directives.unchanged,
        'scripts': directives.unchanged,
        'modules': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        super(Sphinkydoc, self).__init__(*args, **kwargs)
        self.tenv = templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        scripts = []
        module_names = []
        
        if 'scripts' in self.options:
            scripts = quote_split(self.options['scripts'])
            
        if 'modules' in self.options:
            module_names = quote_split(self.options['modules'])
            
        if 'maxdepth' not in self.options:
            self.options['maxdepth'] = -1
            
        #print >> sys.stderr, ("module_names %s" % module_names)
        
        def generate_docs(gen, items):
            for item in items:
                try:
                    yield gen(item)
                except GenerateDocError, e:
                    print >> sys.stderr, "Doc cannot be generated: %s" % e
    
        # Generate recursively all submodules and packages also
        if not 'no-gen' in self.options:
            for module_name in module_names:
                try:
                    self.recursive_generate_module_doc(module_name)
                except GenerateDocError:
                    pass 
        list(generate_docs(self.generate_module_doc, module_names))
        list(generate_docs(self.generate_script_doc, scripts))
        
        module_rows = list(generate_docs(self.module_row, module_names)) 
        script_rows = list(generate_docs(self.script_row, scripts))
        
        # Create toc for all names in table
        toc = self.create_toc([(name, full_name) for name, full_name, _desc in
                               (script_rows + module_rows)])
        
        return [toc] 
            
    def create_toc(self, names):
        """Create toc node entries for names.
        
        """
        tocnode = addnodes.toctree()
        tocnode['includefiles'] = [name for short_name, name in names]
        print >> sys.stderr, "Create toc for %s " % names
        tocnode['entries'] = [(short_name, name) for short_name, name in names]
        tocnode['maxdepth'] = self.options['maxdepth']
        tocnode['glob'] = None
        return tocnode
    
    def recursive_generate_module_doc(self, module_name):
        """Iteratively generates module documentation for all submodules,
        and subpackages.
        
        :param module_name: Module 
        
        """
        
        try:
            module, _name = import_by_name(module_name)
        except ImportError, e:
            raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
        
        try:
            self.generate_module_doc(_name)
        except GenerateDocError:
            pass
        
        for submodule_name in get_submodules(module):
            self.recursive_generate_module_doc(_name + "." + submodule_name)
    
    def generate_module_doc(self, module_name):
        """Generates documentation for module or package.
        
        :param module_name: Full name of the module.
         
        """
        
        try:
            module, name = import_by_name(module_name)
        except ImportError, e:
            raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
        
        members = get_module_members(module)
        template = self.tenv.get_template("sphinkydoc/module.rst")
        
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

    def generate_script_doc(self, script_path):
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
        
        template = self.tenv.get_template("sphinkydoc/script.rst")
        tcontext = {'script_path' : script_path, 'script_name' : script_name, 
                    'help' : help}
        
        file_ = open("%s.rst" % script_name, 'w+')
        file_.write(template.render(tcontext))
        file_.close()
        
    def module_row(self, module_name):
        """Module rows in table.
        
        :returns: reStructuredText tuple that can be used in tables.
        
        """
        try:
            module, name = import_by_name(module_name)
        except ImportError, e:
            raise GenerateDocError("Failed to import '%s': %s" % (module_name, e))
        
        return module_name.split(".")[-1], name, "Doc..."
    
    def script_row(self, script_path):
        """Script rows in table.
        
        :returns: reStructuredText tuple that can be used in tables.
        
        """
        script = os.path.basename(script_path)
        return script, script, "doc..."


class GenerateDocError(Exception):
    """Error during generation of documentation."""
    pass