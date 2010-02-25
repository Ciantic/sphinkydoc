"""Sphinkydoc (Sphinx Extension) 

Extension that is supposed to make Sphinx more ad-hoc for smaller projects.

"""
import sys
__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, Sphinx extension package"
__author__ = "Jari Pennanen"
__license__ = "FreeBSD, see COPYING"

from sphinkydocext import directives, utils
from docutils import nodes

__all__ = ['directives', 'utils', 'setup', 'templating']

def setup(app):
    """Setups the Sphinx extension.
    
    :param app: Sphinx app.
    
    """
    from sphinkydocext.directives.usage import usage_directive
    from sphinkydocext.directives.sphinkydoc import Sphinkydoc, sphinkydoc_toc
    #app.setup_extension('sphinkydocext')
    app.add_node(sphinkydoc_toc)
#    app.connect('doctree-read', process_sphinkydoc_toc)
#    app.connect('builder-inited', process_generate_options)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc', Sphinkydoc)
