# -*- coding: utf-8 -*-

"""Sphinkydoc directive"""
from docutils import nodes
from docutils.parsers.rst import directives
from sphinkydocext.templating import templating_environment, get_module_members, \
    get_submodules
from sphinkydocext.utils import quote_split
from sphinx import addnodes
from sphinx.ext.autosummary import import_by_name
from sphinx.util.compat import Directive
import os
import sys

__all__ = ['sphinkydoc_toc', 'Sphinkydoc']

class sphinkydoc_toc(nodes.comment):
    """Dummy toc node."""
    pass
        
def create_toc(names, maxdepth=-1):
    """Create toc node entries for names.
    
    """
    tocnode = addnodes.toctree()
    tocnode['includefiles'] = [name for short_name, name in names]
    # print >> sys.stderr, "Create toc for %s " % names
    tocnode['entries'] = [(short_name, name) for short_name, name in names]
    tocnode['maxdepth'] = maxdepth
    tocnode['glob'] = None
    return tocnode

class SphinkydocModules(Directive):
    """Sphinkydoc modules directive.
    
    Usage in reStructuredText::
    
        .. sphinkydoc-modules::
            
            firstmod
            secondmod
            thirdmod
    
    """

    final_argument_whitespace = False
    has_content = True
    
    option_spec = {
        'maxdepth': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        super(SphinkydocModules, self).__init__(*args, **kwargs)
        self.tenv = templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        
        # Sphinx configuration env:
        env = self.state.document.settings.env
        
        module_names = self.content
        
        if 'maxdepth' not in self.options:
            self.options['maxdepth'] = -1
            
        module_rows = [self.module_row(m) for m in module_names if m] 
        
        # Create toc for all names in table
        toc = create_toc([(name, full_name) 
                          for name, full_name in module_rows], 
                          self.options['maxdepth'])
        
        return [toc]        
    

    def module_row(self, module_name):
        """Module rows in table.
        
        :returns: reStructuredText tuple that can be used in tables.
        
        """
        try:
            module, name = import_by_name(module_name)
        except ImportError, e:
            raise e #TODO: We probably want to supress the error!
        
        return module_name.split(".")[-1], name


class SphinkydocScripts(Directive):
    """Sphinkydoc directive.
    
    Usage in reStructuredText::
    
        .. sphinkydoc::
            :scripts: firstscript.py secondscript.py "third script.py"
            :modules: firstmod secondmod
    
    """

    final_argument_whitespace = False
    has_content = True
    
    option_spec = {
        'maxdepth': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        super(SphinkydocScripts, self).__init__(*args, **kwargs)
        self.tenv = templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        
        script_paths = self.content
        
        if 'maxdepth' not in self.options:
            self.options['maxdepth'] = -1
            
        script_rows = [self.script_row(s) for s in script_paths if s] 
        
        # Create toc for all names in table
        toc = create_toc([(name, full_name) 
                          for name, full_name in script_rows], 
                          self.options['maxdepth'])
        
        return [toc] 
        
        return [toc] 
    
    def script_row(self, script_path):
        """Script rows in table.
        
        :returns: reStructuredText tuple that can be used in tables.
        
        """
        script = os.path.basename(script_path)
        return script, script
