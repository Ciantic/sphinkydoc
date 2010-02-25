"""Utils for sphinkydoc"""
import re

__all__ = ['quote_split']

def quote_split(str):
    """Splits the string by quotes.
    
    :param str: String to be split.
    
    >>> quote_split('something test "something awesome"')
    ['something', 'test', 'something awesome']
    
    """
    return [p.strip("\" ") for p in re.split("( |[\\\"'].*[\\\"'])", str) if p.strip("\" ")]