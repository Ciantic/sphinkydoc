# -*- coding: utf-8 -*-

"""Sphinkydoc directive"""
from docutils import nodes
from docutils.parsers.rst import directives
from sphinkydocext.templating import templating_environment
from sphinkydocext import log
from sphinx import addnodes
from sphinx.ext.autosummary import import_by_name
from sphinx.util.compat import Directive
import os

class sphinkydoc_toc(nodes.comment):
    """Dummy toc node."""
    pass
        
        
def create_toc(names, maxdepth=-1):
    """Create toc node entries for names.
    
    """
    tocnode = addnodes.toctree()
    tocnode['includefiles'] = [name for _short_name, name in names]
    tocnode['entries'] = [(short_name, name) for short_name, name in names]
    tocnode['maxdepth'] = maxdepth
    tocnode['glob'] = None
    return tocnode


class SphinkydocModules(Directive):
    """Sphinkydoc modules toc-tree directive.
    
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
        # Apparently some old docutils has classic class Directive
        Directive.__init__(self, *args, **kwargs)
        self.tenv = templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        
        module_names = self.content
        maxdepth = -1
        
        if 'maxdepth' in self.options:
            maxdepth = int(self.options['maxdepth'])
            
        module_rows = [self.module_row(m) for m in module_names if m] 
        
        # Create toc for all names in table
        toc = create_toc([(name, full_name) 
                          for name, full_name in module_rows], 
                          maxdepth=maxdepth)
        
        return [toc]        
    
    def module_row(self, module_name):
        """Module rows in table.
        
        :returns: reStructuredText tuple that can be used in toc.
        
        """
#        try:
#            _module, name = import_by_name(module_name)
#        except ImportError, e:
#            log.info('Module %s cannot be imported.' % module_name)
#            
#            #TODO: Error is not raised, should we handle the error?
#            return module_name.split(".")[-1], module_name
        
        return os.path.basename(module_name.split(".")[-1]), module_name


class SphinkydocScripts(Directive):
    """Sphinkydoc scripts toc-tree directive.
    
    Usage in reStructuredText::
    
        .. sphinkydoc-scripts::
        
            firstscript.py 
            secondscript.py 
            ../src/third script.py
    
    """

    final_argument_whitespace = False
    has_content = True
    
    option_spec = {
        'maxdepth': directives.unchanged,
    }
    
    def __init__(self, *args, **kwargs):
        Directive.__init__(self, *args, **kwargs)
        self.tenv = templating_environment()
    
    def run(self):
        """Run the Sphinkydoc rst directive."""
        
        script_paths = self.content
        maxdepth = -1
        
        if 'maxdepth' in self.options:
            maxdepth = self.options['maxdepth']
            
        script_rows = [self.script_row(s) for s in script_paths if s] 
        
        # Create toc for all names in table
        toc = create_toc([(name, full_name) 
                          for name, full_name in script_rows], 
                          maxdepth=maxdepth)
        
        return [toc]
    
    def script_row(self, script_path):
        """Script rows in table.
        
        :returns: reStructuredText tuple that can be used in toc.
        
        """
        script = os.path.basename(script_path)
        return script, script
