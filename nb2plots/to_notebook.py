""" Sphinx extension to convert RST pages to notebooks """

import re
import os
from os.path import (join as pjoin, relpath, splitext,
                     abspath, dirname, exists)

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import set_classes

from sphinx.util.nodes import split_explicit_title, set_role_source_info


def _rel_url(link_path, page_path):
    """ Return ``/`` separated path of `page_path` relative to `link_path`
    """
    page2link = relpath(link_path, page_path)
    if os.sep == '\\':
        page2link = page2link.replace('\\', '/')
    return page2link


def _normalize_whitespace(text):
    return re.sub(r'\s+', '', text)


def clearnotebook(name, rawtext, text, lineno, inliner, options={},
                  content=[]):
    """ Role for building and linking to notebook html pages

    Parameters
    ----------
    name : str
        The role name used in the document.
    rawtext : str
        The entire markup snippet, including the role markup
    text : str
        The text marked with the role.
    lineno : int
        The line number where `rawtext` appears in the input.
    inliner : object
        The inliner instance that called us.
    options : dict, optional
        Directive options for customization.
    content : content, optional
        The directive content for customization.

    Returns
    -------
    nodes : list
        list of nodes to insert into the document. Can be empty.
    messages : list
        list of system messages. Can be empty
    """
    # process options
    # http://docutils.sourceforge.net/docs/howto/rst-roles.html
    evaluate = options.pop('evaluate', False)
    set_classes(options)
    # Get objects from context
    env = inliner.document.settings.env
    # Get title and link
    text = utils.unescape(text)
    has_explicit, title, nb_fname = split_explicit_title(text)
    nb_fname = _normalize_whitespace(nb_fname)
    if nb_fname == '':
        nb_fname = env.docname + '.ipynb'
    refnode = notebook_reference(rawtext, title, reftype=name,
                                 refexplicit=has_explicit)
    # We may need the line number for warnings
    set_role_source_info(inliner, lineno, refnode)
    refnode['reftarget'] = nb_fname
    refnode += nodes.literal(rawtext, title, classes=[name])
    # we also need the source document
    refnode['refdoc'] = env.docname
    refnode['evaluate'] = evaluate
    # result_nodes allow further modification of return values
    return [refnode], []

clearnotebook.options = {'evaluate': directives.flag}


def fullnotebook(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """" Role to force evaluation of notebook when building """
    options['evaluate'] = True
    return clearnotebook(name, rawtext, text, lineno, inliner, options=options,
                         content=content)


class notebook_reference(nodes.reference):
    """Node for notebook references, similar to pending_xref."""


def collect_notebooks(app, doctree, fromdocname):
    for nb_ref in doctree.traverse(notebook_reference):
        # Collect references
        out_file = nb_ref['reftarget']
        # Check for duplicates
        # CHeck for same file, different full / clear
        # Check for different file full / clear
        pass


def write_notebook(docname, outfile, full):
    pass


def write_notebooks(app, exception):
    """ Write notebooks when build has finished """
    if exception is not None:
        return
    env = app.env
    if not hasattr(env, 'notebooks'):
        return
    for docname, out_file, full in env.notebooks:
        write_notebook(docname, out_file, full)


def visit_notebook_node(self, node):
    self.context.append('')


def depart_notebook_node(self, node):
    self.body.append(self.context.pop())


def setup(app):
    app.add_role('clearnotebook', clearnotebook)
    app.add_role('fullnotebook', fullnotebook)
    app.connect('doctree-resolved', collect_notebooks)
    app.connect('build-finished', write_notebooks)
    app.add_node(notebook_reference,
                 html=(visit_notebook_node, depart_notebook_node))
