"""Usage directive"""

from docutils import nodes
from sphinx.util.compat import make_admonition

__all__ = ['usage_directive']

def usage_directive(name, arguments, options, *args): 
    options['class'] = ['usage']
    node = make_admonition(nodes.admonition, 'usage', ['Usage'], options, *args)
    return node
