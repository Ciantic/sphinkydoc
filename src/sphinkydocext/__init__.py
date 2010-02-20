"""SphinkyDoc (Sphinx Extension) 

Extension that is supposed to make Sphinx more ad-hoc, like EpyDoc.

"""
__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__projectname__ = "SphinkyDoc, Sphinx extension package"
__author__ = "Jari Pennanen"
__license__ = "FreeBSD, see COPYING"

from sphinkydocext import directives

__all__ = ['directives', 'setup']

def setup(app):
    from sphinkydocext.directives.usage import usage_directive
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
