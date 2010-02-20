"""This is example package, used in Sphinkydoc"""

__project__ = "Example SphinkyDoc Package"
__copyright__ = "Sphinkydoc, 2010"
__version__ = "0.8.5"
__release__ = "0.8.5 RC1"

import subpackage
import submodule

__all__ = ['SomeClass', 'modulemethod', 'ATTRIBUTE_OF_MODULE', 'submodule', 
           'subpackage']

class SomeClass(object):
    """Class"""
    pass

def modulemethod(arg):
    """Method in example package"""
    pass

ATTRIBUTE_OF_MODULE = True
"""Example attribute"""
