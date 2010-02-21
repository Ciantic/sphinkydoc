# -*- coding: utf-8 -*-

"""Sphinkydoc directive"""
from sphinx.util.compat import Directive
from docutils.parsers.rst import directives
from docutils import nodes

from jinja2 import FileSystemLoader, TemplateNotFound
from jinja2.sandbox import SandboxedEnvironment
from docutils.statemachine import ViewList
from sphinx import addnodes#, roles
import os
#import sys
import shlex
import sys
import re

class sphinkydoc_table(nodes.comment):
    pass

def quote_split(str):
    return [p for p in re.split("( |[\\\"'].*[\\\"'])", str) if p.strip()]

class Sphinkydoc(Directive):
    """Sphinkydoc directive.
    
    .. usage::
    
        ::
        
            .. sphinkydoc::
                :scripts: firstscript.py secondscript.py "third script.py"
                :modules: firstmod secondmod
    
    """
    
    option_spec = {
        'scripts': directives.unchanged,
        'modules': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        super(Sphinkydoc, self).__init__(*args, **kwargs)
        self.tenv = self.templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        scripts = []
        modules = []
        
        if 'scripts' in self.options:
            scripts = quote_split(self.options['scripts'])
            
        if 'modules' in self.options:
            modules = quote_split(self.options['modules'])
            
        print >> sys.stderr, ("modules %s" % modules)
            
        module_rows = [self.generate_module_doc(mod) for mod in modules]
        script_rows = [self.generate_script_doc(scr) for scr in scripts]
        
        # Create table
        table = self.get_table(script_rows=script_rows, module_rows=module_rows)
        
        # Create toc for all names in table
        toc = self.create_toc([name for name, _desc in
                               module_rows + script_rows])
        
        return table + toc
    
    def templating_environment(self):
        """Jinja2 templating environment.
        
        :returns: :obj:`jinja2.environment.Environment`
        
        """
        # create our own templating environment
        template_dirs = [os.path.realpath(
                            os.path.join(os.path.dirname(__file__) + "/../", 
                                         'templates')
                        )]
        print >> sys.stderr, template_dirs
        #if builder is not None:
        #    # allow the user to override the templates
        #    template_loader = BuiltinTemplateLoader()
        #    template_loader.init(builder, dirs=template_dirs)
        #else:
        #    if template_dir:
        #        template_dirs.insert(0, template_dir)
        template_loader = FileSystemLoader(template_dirs)
        return SandboxedEnvironment(loader=template_loader)
            
    def create_toc(self, names):
        """Create toc node entries for names.
        
        """
        tocnode = addnodes.toctree()
        tocnode['includefiles'] = names
        tocnode['entries'] = [(None, name) for name in names]
        tocnode['maxdepth'] = -1
        tocnode['glob'] = None
        return tocnode
    
    def generate_module_doc(self, module):
        """Generates documentation for module or package recursively upwards.
        
        :param module: Name of the module.
        :returns: reStructuredText tuple that can be used in tables.
         
        """
        template = self.tenv.get_template("module.rst")
        print >> sys.stderr, ("Testing templates... %s " % module)
        
        if not os.path.exists(module):  
            os.mkdir(module)
            
        f = open("%s/index.rst" % module, 'w+')
        f.write(template.render({ 'module' : module }))
        f.close()
                    
        return module, "Doc..."
    
    def generate_script_doc(self, script):
        """Generates documentation for script.
        
        :param module: Path to script.
        :returns: reStructuredText tuple that can be used in tables.
         
        """
        return os.path.basename(script), "doc..."
    
    def get_table(self, module_rows=None, script_rows=None):
        """Get rst table.
        
        """ 
        table_spec = addnodes.tabular_col_spec()
        table_spec['spec'] = 'LL'

        table = nodes.table('')
        
        group = nodes.tgroup('', cols=2)
        group.append(nodes.colspec('', colwidth=10))
        group.append(nodes.colspec('', colwidth=90))
        body = nodes.tbody('')
        group.append(body)
        table.append(group)
        
        # Geez, who the hell forgot to create high level api for docutils?
        def append_row(*column_texts):
            row = nodes.row('')
            for text in column_texts:
                node = nodes.paragraph('')
                vl = ViewList()
                vl.append(text, '<sphinkydoc>')
                self.state.nested_parse(vl, 0, node)
                try:
                    if isinstance(node[0], nodes.paragraph):
                        node = node[0]
                except IndexError:
                    pass
                row.append(nodes.entry('', node))
            body.append(row)
        
        for name, desc in module_rows:
            append_row(":mod:`%s`" % name, desc)
            
        for name, desc in script_rows:
            append_row(":exec:`%s`" % name, desc)

        #sphinky_table = sphinkydoc_table('')
        #sphinky_table.append(table)
        
        return [table]
