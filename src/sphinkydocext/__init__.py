"""Sphinkydoc (Sphinx Extension) 

Extension that is supposed to make Sphinx more ad-hoc for smaller projects.

"""
import sys
__version__ = "0.5.5"
__release__ = "0.5.5 alpha"
__copyright__ = "Jari Pennanen, 2010"
__project__ = "Sphinkydoc, Sphinx extension package"
__author__ = "Jari Pennanen"
__license__ = "FreeBSD, see COPYING"

from sphinkydocext import directives, utils
from docutils import nodes

__all__ = ['directives', 'utils', 'setup']

#def process_sphinkydoc_toc(app, doctree):
#    """
#    Insert items described in autosummary:: to the TOC tree, but do
#    not generate the toctree:: list.
#    """
#    env = app.builder.env
#    crawled = {}
#    def crawl_toc(node, depth=1):
#        crawled[node] = True
#        for j, subnode in enumerate(node):
#            print >> sys.stderr, "Enumerating node..."
#            try:
#                pass
#                #if (isinstance(subnode, autosummary_toc)
#                #    and isinstance(subnode[0], addnodes.toctree)):
#                #    env.note_toctree(env.docname, subnode[0])
#                #    continue
#            except IndexError:
#                continue
#            if not isinstance(subnode, nodes.section):
#                continue
#            if subnode not in crawled:
#                crawl_toc(subnode, depth+1)
#    crawl_toc(doctree)
#
#def process_generate_options(app):
#    genfiles = app.config.autosummary_generate
#
#    ext = app.config.source_suffix
#
#    if genfiles and not hasattr(genfiles, '__len__'):
#        env = app.builder.env
#        genfiles = [x + ext for x in env.found_docs
#                    if os.path.isfile(env.doc2path(x))]
#
#    if not genfiles:
#        return
#
#    from sphinx.ext.autosummary.generate import generate_autosummary_docs
#
#    genfiles = [genfile + (not genfile.endswith(ext) and ext or '')
#                for genfile in genfiles]
#
#    generate_autosummary_docs(genfiles, builder=app.builder,
#                              warn=app.warn, info=app.info, suffix=ext,
#                              base_path=app.srcdir)
#    
def setup(app):
    from sphinkydocext.directives.usage import usage_directive
    from sphinkydocext.directives.sphinkydoc import Sphinkydoc, sphinkydoc_toc
    #app.setup_extension('sphinkydocext')
    app.add_node(sphinkydoc_toc)
#    app.connect('doctree-read', process_sphinkydoc_toc)
#    app.connect('builder-inited', process_generate_options)
    app.add_directive('usage', usage_directive, 1, (0, 1, 1))
    app.add_directive('sphinkydoc', Sphinkydoc)
