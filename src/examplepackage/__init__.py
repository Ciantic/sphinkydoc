"""This is example package, demonstrating the automatically generated docs."""
__project__ = "Example SphinkyDoc Package"
__copyright__ = "Sphinkydoc, 2010"
__version__ = "0.8.5"
__release__ = "0.8.5 RC1"

# Pylint disable settings --------------------------
#
# Docstrings, unused args:
# pylint: disable-msg=W0105, W0613
#

import subpackage
import submodule

__all__ = ['SomeClass', 'modulemethod', 'ATTRIBUTE_OF_MODULE', 'submodule', 
           'subpackage']

class SomeClass(object):
    """Class docstring"""
    
    some_attribute = False
    """Some attribute in some class...
    
    :type: bool
    """
    
    some_other_attribute = ""
    """Some other attribute, should be string."""


def modulemethod(arg): 
    """Method in example package"""
    
ATTRIBUTE_OF_MODULE = True
"""Example attribute docstring"""
