"""Sphinkydocext -- Sphinx Extension of Sphinkydoc 

This is Sphinx extension that is supposed to make Sphinx more ad-hoc for smaller
projects. When using :ref:`sphinkydoc.py` as documentation builder you don't 
have to specify any settings, the script creates Sphinx configurations itself.

Usage in existing Sphinx project
================================

Using this as extension, it is assumed that one understands the basics of Sphinx
documentation generator.

Since main purpose of :mod:`sphinkydocext` is to generate documentation files,
and having generated files in same place as written documentation files makes
the development a messy, this is unfortunately unavoidable at the moment.

It would be possible to put the generated files in another directory if Sphinx
allowed to have several root docs directories. Meanwhile as it is not allowed,
the generated files has to appear to root of Sphinx configuration.

Sphinx conf.py variables
------------------------
    
Docs generation
'''''''''''''''

.. confval:: sphinkydoc_modules

    List of module names which documentation is generated using
    :func:`~sphinkydocext.generate.module_doc`, defaults to empty list.

.. confval:: sphinkydoc_modules_overwrite

    Overwrite the existing generated module API files? Defaults to
    :const:`False`.
    
.. confval:: sphinkydoc_scripts

    List of paths to scripts which documentation is generated using
    :func:`~sphinkydocext.generate.script_doc`, defaults to empty list.

.. confval:: sphinkydoc_scripts_overwrite

    Overwrite the existing generated scripts files? Defaults to :const:`False`.
    
.. confval:: sphinkydoc_index

    Indicating whether `index.rst` should be generated using
    :func:`~sphinkydocext.generate.index_doc`, defaults to :const:`False`.
    
.. confval:: sphinkydoc_readme_html

    Indicating whether `README.html` should be generated to caps directory using
    :func:`~sphinkydocext.generate.readme_html_doc`, defaults to :const:`False`.

Special directories
'''''''''''''''''''
        
.. confval:: sphinkydoc_modules_dir
    
    Directory where to *output* the generated module docs as
    ``module.submodule.rst``. **Must be relative to sources directory.**
    Defaults to root of source directory.
    
.. confval:: sphinkydoc_scripts_dir

    Directory where to *output* the generated script docs as ``script.py.rst``.
    **Must be relative to sources directory.** Defaults to root of source
    directory.

.. confval:: sphinkydoc_docs_dir

    Directory of *additional docs* directory, files from this directory are
    copied to Sphinx configuration directory before building, defaults to
    :const:`None` and is not used.     
    
    .. warning:: Do not try to set this as same directory as your Sphinx
        configuration directory.
    
.. confval:: sphinkydoc_caps_dir

    Directory of :term:`caps-files`, defaults to :const:`None` and is not used.

.. note:: Relative paths are converted to absolute during `builder-init`, and
    thus should be safe to use.

Files in caps dir
'''''''''''''''''

These options *require* that :confval:`sphinkydoc_caps_dir` is set.
    
.. confval:: sphinkydoc_caps_literals

    List of :term:`caps-files` that are treated as literally, defaults to
    [:data:`COPYING`].
    
.. confval:: sphinkydoc_caps_included

    List of :term:`caps-files` that are included and doesn't have a separate
    page, defaults to [``'README'``].
    
.. confval:: sphinkydoc_caps_about

    List of :term:`caps-files` that are categorized as About, defaults to
    [``'AUTHORS'``, ``'THANKS'``, :data:`COPYING`, ``'LICENSE'``].
    
.. confval:: sphinkydoc_caps_topic

    List of :term:`caps-files` that are categorized as Topic, defaults to
    [:data:`ALL`].
    
Files in docs dir
'''''''''''''''''

These options require that :confval:`sphinkydoc_docs_dir` is set.
    
.. confval:: sphinkydoc_included

    List of normal docs files that are included and doesn't have a separate
    page, defaults to empty list.
    
.. confval:: sphinkydoc_about

    List of normal docs files that are categorized as About, defaults to empty
    list.
    
.. confval:: sphinkydoc_topic

    List of normal docs files that are categorized as Topic, defaults to
    [:data:`ALL_ROOT`, :data:`ALL_SUBINDEX`].
    
"""
import logging
import os
logging.basicConfig()

log = logging.getLogger("sphinkydoc")
"""Sphinkydoc logger"""

log.setLevel(logging.WARNING)

from sphinkydocext import directives, utils, templating, generate
from sphinkydocext.generate import caps_doc
from sphinkydocext.templating import templating_environment
from sphinkydocext.utils import copy_tree, multi_matcher, path_to_posix, \
    truncate_path, directory_slash_suffix
import re
import sys


__version__ = "0.5.6"
__release__ = "0.5.6 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, generates documentation for whole packages"

__all__ = ['directives', 'utils', 'setup', 'templating', 'generate', 
           'COPYING', 'ALL', 'ALL_ROOT', 'ALL_SUBINDEX', 'log']

# Pylint-disable settings ----------------
# Todo, Strings, Unused, Map:
#     pylint: disable-msg=W0511,W0105,W0613,W0141

COPYING = re.compile('^COPYING(\..*)?$')
"""Matches all COPYING.* files"""

ALL = re.compile('')
"""Matches anything."""

ALL_ROOT = re.compile('^[^/]+$')
"""Matches any file in root directory"""

ALL_SUBINDEX = re.compile('.*/index$') # Amazingly ".*" is required.
"""Matches all subdirectory index files"""

THEMES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'themes'))
"""Additional themes provided by sphinkydoc"""

def builder_inited(app):
    """Sphinx builder-inited callback handler.
    
    :param app: Sphinx app.
    
    """
    conf = app.config
    
    truncate_path_rst = lambda p: truncate_path(p, directory=app.srcdir, 
                                                extension='rst')
    tenv = templating_environment()
    caps_files = []
    docs_files = []
    
    # Gather configuration directories
    docs_dir = conf.sphinkydoc_docs_dir
    caps_dir = conf.sphinkydoc_caps_dir
    module_dir = directory_slash_suffix(conf.sphinkydoc_modules_dir)
    script_dir = directory_slash_suffix(conf.sphinkydoc_scripts_dir)
    
    # Create relative pathed script and module dirs
    try:
        os.makedirs(os.path.join(app.srcdir, module_dir))
    except os.error:
        pass
    
    try:
        os.makedirs(os.path.join(app.srcdir, script_dir))
    except os.error:
        pass
    
    # Convert paths to abspaths if they are not already
    if docs_dir:
        docs_dir = os.path.abspath(docs_dir)
        
    if caps_dir:
        caps_dir = os.path.abspath(caps_dir)
    
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
    if docs_dir and os.path.abspath(app.srcdir) != docs_dir:
        _files = copy_tree(docs_dir, app.srcdir, skip_dirs=['html', '_temp'])
        docs_files = filter(lambda p: not p.endswith('.rst'), 
                            map(truncate_path_rst, _files))    
    # Caps files generation
    if caps_dir:
        _files = caps_doc(tenv, caps_dir, ext="rst", 
                          caps_literals=conf.sphinkydoc_caps_literals, 
                          output_dir=app.srcdir)
        caps_files = filter(lambda p: not p.endswith('.rst'), 
                            map(truncate_path_rst, _files))
        
    # Should we generate HTML shortcut file to caps directory?
    if conf.sphinkydoc_readme_html and caps_dir:
        generate.readme_html_doc(tenv, "docs/html/index.html", 
                                 output_dir=caps_dir)
        
    # Notice that following generates nothing, if the lists are empty:
    _module_files, _script_files = \
        generate.all_doc(tenv, conf.sphinkydoc_modules, conf.sphinkydoc_scripts,
                         module_output_dir=module_dir, 
                         module_overwrite=conf.sphinkydoc_modules_overwrite,
                         script_output_dir=script_dir,
                         script_overwrite=conf.sphinkydoc_scripts_overwrite,
                         source_dir=os.path.abspath(app.srcdir))
        
    module_files = map(truncate_path_rst, _module_files)
    script_files = map(truncate_path_rst, _script_files)
    
    module_files = map(path_to_posix, module_files)
    script_files = map(path_to_posix, script_files)    
    docs_files = map(path_to_posix, docs_files)
    caps_files = map(path_to_posix, caps_files)
    
    for s in set(script_files + module_files).intersection(set(docs_files)):
        docs_files.remove(s)
    
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
    
    # Index generation
    if conf.sphinkydoc_index:
        tcontext = {
            'caps_files' : caps_files,
            'docs_files' : docs_files,
            'modules_dir' : module_dir,
            'scripts_dir' : script_dir,
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
        
    app.config.html_theme_path.append(THEMES_DIR)
    app.add_config_value('sphinkydoc_caps_literals', [COPYING], '')
    
    app.add_config_value('sphinkydoc_caps_included', ['README'], '')
    app.add_config_value('sphinkydoc_caps_about', 
        ['AUTHORS', 'THANKS', COPYING, 'LICENSE'], '')
    app.add_config_value('sphinkydoc_caps_topic', [ALL], '')
    
    app.add_config_value('sphinkydoc_included', [], '')
    app.add_config_value('sphinkydoc_about', [], '')
    app.add_config_value('sphinkydoc_topic', [ALL_ROOT, ALL_SUBINDEX], '')
    
    app.add_config_value('sphinkydoc_modules', [], '')
    app.add_config_value('sphinkydoc_modules_overwrite', False, '')
    app.add_config_value('sphinkydoc_scripts', [], '')
    app.add_config_value('sphinkydoc_scripts_overwrite', False, '')
    app.add_config_value('sphinkydoc_index', False, '')
    app.add_config_value('sphinkydoc_readme_html', False, '')
    app.add_config_value('sphinkydoc_docs_dir', None, '')
    app.add_config_value('sphinkydoc_modules_dir', "", '')
    app.add_config_value('sphinkydoc_scripts_dir', "", '')
    app.add_config_value('sphinkydoc_caps_dir', None, '')
    app.add_config_value('sphinkydoc_debug', False, '')

    app.add_description_unit('confval', 'confval', 
                             'pair: %s; configuration value')
    
    app.add_description_unit('program-usage', 'program-usage')
    
    app.add_node(sphinkydoc_toc)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc-scripts', SphinkydocScripts)
    app.add_directive('sphinkydoc-modules', SphinkydocModules)
    
    # Debugging settings
    if app.config.sphinkydoc_debug:
        log.setLevel(logging.INFO)
    
    app.connect('builder-inited', builder_inited)
