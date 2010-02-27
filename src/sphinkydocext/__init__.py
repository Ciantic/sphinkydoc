"""Sphinkydoc (Sphinx Extension) 

This is Sphinx extension that is supposed to make Sphinx more ad-hoc for smaller
projects. When using :ref:`sphinkydoc.py` as documentation builder you don't 
have to specify any settings, the script does them automatically.

Usage in Sphinx project
-----------------------

.. todo:: To be described...

"""
from sphinkydocext import directives, utils, templating, generate
from sphinkydocext.generate import caps_doc
from sphinkydocext.templating import templating_environment
from sphinkydocext.utils import copy_tree, multi_matcher, path_to_posix
import re
import sys

__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, generates documentation for whole packages"

__all__ = ['directives', 'utils', 'setup', 'templating', 'generate']


def builder_inited(app):
    """Sphinx builder-inited callback handler.
    
    :param app: Sphinx app.
    
    """
    conf = app.config
    
    tenv = templating_environment()
    caps_files = []
    docs_files = []
    
    categorized = {}
    # Order of the items in category matchers, one could put this in the list of
    # matchers as tuples but then redefining the order becomes cumbersome.
    category_order = ('included', 'about', 'topic')
    
    category_matchers_caps = {
        'included': multi_matcher(conf.sphinkydoc_caps_included),
        'about': multi_matcher(conf.sphinkydoc_caps_about),
        'topic': multi_matcher(conf.sphinkydoc_caps_topic),
    }
    
    category_matchers = {
        'included': multi_matcher(conf.sphinkydoc_included),
        'about': multi_matcher(conf.sphinkydoc_about),
        'topic': multi_matcher(conf.sphinkydoc_topic),
    }
    
    # Additional docs copier
    if conf.sphinkydoc_docs_dir:
        _files = copy_tree(conf.sphinkydoc_docs_dir, app.srcdir, 
                               skip_dirs=['html', '_temp'])
        
        docs_files = [n[len(app.srcdir)+1:-4] 
                      for n in _files if n.endswith(".rst")]
    
    # Caps files generation
    if conf.sphinkydoc_caps_dir:
        caps_files = caps_doc(tenv, conf.sphinkydoc_caps_dir, ext="rst", 
                              caps_literals=conf.sphinkydoc_caps_literal, 
                              output_dir=app.srcdir)
    
    docs_files = [path_to_posix(fp) for fp in docs_files]
    caps_files = [path_to_posix(fp) for fp in caps_files]
    
    def categorize(_files, category_matchers):
        # Categorizes the items to dictionary (always to first matching category) 
        for n in _files:
            for cat in category_order:
                if category_matchers[cat](n):
                    categorized.setdefault("%s_files" % cat, []).append(n)
                    break
                
    categorize(caps_files, category_matchers_caps)
    categorize(docs_files, category_matchers)
            
    # Included docs should have different extension
    for inc in categorized.get('included_files', []):
        generate.included_doc(tenv, inc, app.srcdir)
        
    # Conf unused docs does not work for included files, graah...
    # conf.unused_docs.extend(['README.rst']#.extend(categorized.get('included', [])) 

    # Notice that following generates nothing, if the lists are empty:
    generate.all_doc(tenv, conf.sphinkydoc_modules, 
                     conf.sphinkydoc_scripts, output_dir=app.srcdir)
    
    # print >> sys.stderr, "Docs files: %s" % docs_files
    # print >> sys.stderr, "Caps files: %s" % caps_files
    
    # Index generation
    if conf.sphinkydoc_index:
        tcontext = {
            'caps_files' : caps_files,
            'docs_files' : docs_files,
            'scripts' : conf.sphinkydoc_scripts,
            'modules' : conf.sphinkydoc_modules,
        }
        
        tcontext.update(categorized)
        
        generate.index_doc(tenv, tcontext, output_dir=app.srcdir)


def setup(app):
    """Setups the Sphinx extension.
    
    :param app: Sphinx app.
    
    """
    from sphinkydocext.directives.usage import usage_directive
    from sphinkydocext.directives.sphinkydoc import SphinkydocModules, \
        SphinkydocScripts, sphinkydoc_toc
        
    COPYING = re.compile('^COPYING(\..*)?$')
    ALL = re.compile('')
    ALL_ROOT = re.compile('^[^/]+$')
    ALL_SUBINDEX = re.compile('.*/index$') # Amazingly ".*" is required.
    
    app.add_config_value('sphinkydoc_caps_literal', [COPYING], '')
    
    app.add_config_value('sphinkydoc_caps_included', ['README'], '')
    app.add_config_value('sphinkydoc_caps_about', 
        ['AUTHORS', 'THANKS', COPYING, 'LICENSE'], '')
    app.add_config_value('sphinkydoc_caps_topic', [ALL], '')
    
    app.add_config_value('sphinkydoc_included', [], '')
    app.add_config_value('sphinkydoc_about', [], '')
    app.add_config_value('sphinkydoc_topic', [ALL_ROOT, ALL_SUBINDEX], '')
    
    app.add_config_value('sphinkydoc_modules', [], '')
    app.add_config_value('sphinkydoc_scripts', [], '')
    
    app.add_config_value('sphinkydoc_index', False, '')
    app.add_config_value('sphinkydoc_docs_dir', None, '')
    app.add_config_value('sphinkydoc_caps_dir', None, '')
    #app.add_config_value('sphinkydoc_magic_files', )
    #app.setup_extension('sphinkydocext')
    app.connect('builder-inited', builder_inited)
    app.add_node(sphinkydoc_toc)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc-scripts', SphinkydocScripts)
    app.add_directive('sphinkydoc-modules', SphinkydocModules)
