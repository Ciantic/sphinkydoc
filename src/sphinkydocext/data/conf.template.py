# -*- coding: utf-8 -*-

# Sphinkydoc template file for sphinx conf.py.
# pylint: disable-msg-cat=WCREFI
 
import sys
import os

{% for module in modules %} 
import {{ module }}
{% endfor %}

project =  {{ project }}
copyright = {{ copyright }}
version = {{ version }}
release = {{ release }}

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
              'sphinx.ext.autosummary', 'sphinkydocext']

templates_path = ['templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_trees = ['templates']
pygments_style = 'sphinx'

# HTML ---------------------------------------

html_theme = 'default'
html_static_path = ['static']

# Autodoc ------------------------------------

# autoclass_content = "both"
autodoc_member_order = "groupwise"
autosummary_generate = True

# Todo ------------------------------------

todo_include_todos = False

def non_init_skip(app, what, name, obj, skip, options):
    """Otherwise normally, but don't skip init."""
    if skip and name == '__init__':
        return False
    return skip

def setup(app):
    app.connect('autodoc-skip-member', non_init_skip)
