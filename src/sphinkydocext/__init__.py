"""Sphinkydoc (Sphinx Extension) 

This is Sphinx extension that is supposed to make Sphinx more ad-hoc for smaller
projects. When using :ref:`sphinkydoc.py` as documentation builder you don't 
have to specify any settings, the script creates Sphinx configurations itself.

Usage in existing Sphinx project
================================

In case one decided to use this as extension, it is assumed that one understands
the basics of Sphinx documentation generator.

Since main purpose of :mod:`sphinkydocext` is to generate documentation files,
and having generated files in same place as written documentation files makes
the development a messy, this is unfortunately unavoidable at the moment.

It would be possible to put the generated files in another directory if Sphinx
allowed to have several root docs directories. Meanwhile as it is not allowed,
the generated files has to appear to root of Sphinx configuration.

Sphinx conf.py variables
------------------------
    
.. rubric:: Docs generation
    
:ref:`sphinkydoc_modules`
    List of module names which documentation is generated using
    :func:`~sphinkydocext.generate.module_doc`, defaults to empty list.
    
:ref:`sphinkydoc_scripts`
    List of paths to scripts which documentation is generated using
    :func:`~sphinkydocext.generate.script_doc`, defaults to empty list.
    
:ref:`sphinkydoc_index`
    Indicating whether `index.rst` should be generated using
    :func:`~sphinkydocext.generate.index_doc`, defaults to :const:`False`.
    
:ref:`sphinkydoc_readme_html`
    Indicating whether `README.html` should be generated to caps directory using
    :func:`~sphinkydocext.generate.readme_html_doc`, defaults to :const:`False`.

.. rubric:: Special directories
    
:ref:`sphinkydoc_docs_dir`
    Directory of *additional docs* directory, files from this directory are
    copied to Sphinx configuration directory before building, defaults to
    :const:`None` and is not used. 
    
    .. warning:: Do not try to set this as same directory as your Sphinx
        configuration directory.
    
:ref:`sphinkydoc_caps_dir`
    Directory of :term:`caps-files<caps-file>`, defaults to :const:`None` and is
    not used.

.. rubric:: Files in caps dir

These options require that `sphinkydoc_caps_dir` is set.
    
:ref:`sphinkydoc_caps_literal`
    List of :term:`caps files<caps-file>` that are treated as literally,
    defaults to [:data:`COPYING`].
    
:ref:`sphinkydoc_caps_included`
    List of :term:`caps files<caps-file>` that are included and doesn't have
    a separate page, defaults to [``'README'``].
    
:ref:`sphinkydoc_caps_about`
    List of :term:`caps files<caps-file>` that are categorized as About,
    defaults to [``'AUTHORS'``, ``'THANKS'``, :data:`COPYING`,
    ``'LICENSE'``].
    
:ref:`sphinkydoc_caps_topic`
    List of :term:`caps files<caps-file>` that are categorized as Topic,
    defaults to [:data:`ALL`].
    
.. rubric:: Files in docs dir

These options require that `sphinkydoc_docs_dir` is set.
    
:ref:`sphinkydoc_included`
    List of normal docs files that are included and doesn't have a separate
    page, defaults to empty list.
    
:ref:`sphinkydoc_about`
    List of normal docs files that are categorized as About, defaults to empty
    list.
    
:ref:`sphinkydoc_topic`
    List of normal docs files that are categorized as Topic, defaults to
    [:data:`ALL_ROOT`, :data:`ALL_SUBINDEX`].
    
"""
import logging
logging.basicConfig()
log = logging.getLogger("sphinkydoc")
log.setLevel(logging.INFO) # TODO: DEBUG!

from sphinkydocext import directives, utils, templating, generate
from sphinkydocext.generate import caps_doc
from sphinkydocext.templating import templating_environment
from sphinkydocext.utils import copy_tree, multi_matcher, path_to_posix,\
    truncate_path
import re
import sys

__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, generates documentation for whole packages"

__all__ = ['directives', 'utils', 'setup', 'templating', 'generate', 
           'COPYING', 'ALL', 'ALL_ROOT', 'ALL_SUBINDEX', 'log']

# Pylint-disable settings ----------------
# Todo, Strings, Unused:
#     pylint: disable-msg=W0511,W0105,W0613

COPYING = re.compile('^COPYING(\..*)?$')
"""Matches all COPYING.* files"""

ALL = re.compile('')
"""Matches anything."""

ALL_ROOT = re.compile('^[^/]+$')
"""Matches any file in root directory"""

ALL_SUBINDEX = re.compile('.*/index$') # Amazingly ".*" is required.
"""Matches all subdirectory index files"""

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
        
        docs_files = [truncate_path(p, app.srcdir, 'rst') 
                      for p in _files if p.endswith('.rst')]
    
    # Caps files generation
    if conf.sphinkydoc_caps_dir:
        _files = caps_doc(tenv, conf.sphinkydoc_caps_dir, ext="rst", 
                          caps_literals=conf.sphinkydoc_caps_literal, 
                          output_dir=app.srcdir)
        caps_files = [truncate_path(p, app.srcdir, 'rst')
                      for p in _files if p.endswith('.rst')]
        
    # Should we generate HTML shortcut file to caps directory?
    if conf.sphinkydoc_readme_html and conf.sphinkydoc_caps_dir:
        generate.readme_html_doc(tenv, "docs/html/index.html", 
                                 output_dir=conf.sphinkydoc_caps_dir)
        
    # Notice that following generates nothing, if the lists are empty:
    _module_files, _script_files = \
        generate.all_doc(tenv, conf.sphinkydoc_modules, conf.sphinkydoc_scripts,
                         output_dir=app.srcdir)
        
    module_files = [truncate_path(p, app.srcdir, 'rst') for p in _module_files]
    script_files = [truncate_path(p, app.srcdir, 'rst') for p in _script_files]
    
    module_files = [path_to_posix(fp) for fp in module_files]
    script_files = [path_to_posix(fp) for fp in script_files]    
    docs_files = [path_to_posix(fp) for fp in docs_files]
    caps_files = [path_to_posix(fp) for fp in caps_files]
    
    for s in set(script_files + module_files).intersection(set(docs_files)):
        docs_files.remove(s)
    
    def categorize(_files, category_matchers):
        # Categorizes the items to dictionary (always to first matching category) 
        for n in _files:
            print >> sys.stderr, "Categorizing: %s" % n
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
    # conf.unused_docs.extend(['README.rst']) 

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
    app.add_config_value('sphinkydoc_readme_html', False, '')
    app.add_config_value('sphinkydoc_docs_dir', None, '')
    app.add_config_value('sphinkydoc_caps_dir', None, '')
    #app.add_config_value('sphinkydoc_magic_files', )
    #app.setup_extension('sphinkydocext')
    app.connect('builder-inited', builder_inited)
    app.add_node(sphinkydoc_toc)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc-scripts', SphinkydocScripts)
    app.add_directive('sphinkydoc-modules', SphinkydocModules)
