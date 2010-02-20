# -*- coding: utf-8 -*-
import sys
import os
import $yourmodule as module

# Note, this file is not supposed to be imported.
    
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest', 'sphinx.ext.todo',
              'sphinx.ext.autosummary', 'sphinkydocext']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = module.__project__
copyright = module.__copyright__
version = module.__version__
release = module.__release__
exclude_trees = ['_build', '_templates']
pygments_style = 'sphinx'

# HTML ---------------------------------------

html_theme = 'default'
html_static_path = ['_static']

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
