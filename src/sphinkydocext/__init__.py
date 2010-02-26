"""Sphinkydoc (Sphinx Extension) 

Extension that is supposed to make Sphinx more ad-hoc for smaller projects.

"""
from sphinkydocext.templating import templating_environment

__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, Sphinx extension package"
__author__ = "Jari Pennanen"
__license__ = "FreeBSD, see COPYING"

from sphinkydocext import directives, utils, templating, generate
import sys

__all__ = ['directives', 'utils', 'setup', 'templating']

def builder_inited(app):
    tenv = templating_environment()
    #app.config.unused_docs.extend(app.config.sphinkydoc_magic_included)
    generate.all_doc(tenv, app.config.sphinkydoc_modules, 
                     app.config.sphinkydoc_scripts)

def setup(app):
    """Setups the Sphinx extension.
    
    :param app: Sphinx app.
    
    """
    from sphinkydocext.directives.usage import usage_directive
    from sphinkydocext.directives.sphinkydoc import SphinkydocModules, \
        SphinkydocScripts, sphinkydoc_toc
    
    app.add_config_value('sphinkydoc_magic_about', 
        ['COPYING', 'COPYING.LIB', 'COPYING.LESSER', 'LICENSE','AUTHORS', 
         'THANKS'], '')
    app.add_config_value('sphinkydoc_magic_included', ['README'], '')
    app.add_config_value('sphinkydoc_modules', [], '')
    app.add_config_value('sphinkydoc_scripts', [], '')
    #app.add_config_value('sphinkydoc_magic_files', )
    #app.setup_extension('sphinkydocext')
    app.connect('builder-inited', builder_inited)
    app.add_node(sphinkydoc_toc)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc-scripts', SphinkydocScripts)
    app.add_directive('sphinkydoc-modules', SphinkydocModules)
