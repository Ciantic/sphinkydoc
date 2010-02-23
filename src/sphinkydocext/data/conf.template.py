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

scripts = [{% for script in scripts %} "{{ script }}", {% endfor %}]
    
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
    """
    Otherwise normally, but don't skip init. 
    """
    if skip and name == '__init__':
        return False
    return skip

def setup(app):
    import shutil

    if os.path.exists("api"):
        print "Deleting old api..."
        try:
            shutil.rmtree("api")
        except (IOError, WindowsError), e:
            print >> sys.stderr, "Error: Cannot delete 'api' directory."
            sys.exit(0)
    
    if os.path.exists("_build"):
        print "Deleting old build..."
        try:
            shutil.rmtree("_build")
        except (IOError, WindowsError), e:
            print >> sys.stderr, "Error: Cannot delete '_build' directory."
            sys.exit(0)
            
    app.connect('autodoc-skip-member', non_init_skip)
