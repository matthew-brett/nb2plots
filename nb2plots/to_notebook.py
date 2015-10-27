""" Sphinx extension to convert RST pages to notebooks """

import re
import os
from os.path import (join as pjoin, relpath, splitext,
                     abspath, dirname, exists)
import pickle

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import set_classes

from sphinx.util.nodes import split_explicit_title, set_role_source_info
from sphinx.errors import ExtensionError

# Use notebook format version 4
from .ipython_shim import nbformat
nbf = nbformat.v4


class ToNotebookError(ExtensionError):
    """ Error for notebook sphinx extension """


def _normalize_whitespace(text):
    return re.sub(r'\s+', '', text)


class notebook_reference(nodes.reference):
    """Node for notebook references, similar to pending_xref."""


def clearnotebook(name, rawtext, text, lineno, inliner, options={},
                  content=[]):
    """ Role for building and linking to IPython notebooks

    Parameters
    ----------
    name : str
        The role name used in the document.
    rawtext : str
        The entire markup snippet, including the role markup.
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
        list of system messages. Can be empty.
    """
    # process options
    # http://docutils.sourceforge.net/docs/howto/rst-roles.html
    evaluate = options.pop('evaluate', False)
    set_classes(options)
    # Get objects from context
    env = inliner.document.settings.env
    # Get title and link
    text = utils.unescape(text)
    if text.strip() == '.':
      text = 'Download this page as IPython notebook'
    has_nb_fname, title, nb_fname = split_explicit_title(text)
    if not has_nb_fname:
        nb_fname = env.docname + '.ipynb'
    refnode = notebook_reference(rawtext, title, reftype=name)
    # We may need the line number for warnings
    set_role_source_info(inliner, lineno, refnode)
    refnode['reftarget'] = nb_fname
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


def collect_notebooks(app, doctree, fromdocname):
    env = app.env
    out_notebooks = {}
    for nb_ref in doctree.traverse(notebook_reference):
        # Calculate relative filename
        rel_fn, _  = env.relfn2path(nb_ref['reftarget'], fromdocname)
        # Check for duplicates
        evaluate = nb_ref['evaluate']
        if rel_fn not in out_notebooks:
            out_notebooks[rel_fn] = evaluate
        elif out_notebooks[rel_fn] != evaluate:
            raise ToNotebookError('Notebook filename {0} cannot be both '
                                  'clear and full'.format(rel_fn))
        nb_ref['filename'] = rel_fn
    if len(out_notebooks) == 0:
        return
    to_build = dict(clear=[], full=[])
    for rel_fn, evaluate in out_notebooks.items():
        key = 'full' if evaluate else 'clear'
        to_build[key].append(rel_fn)
    if not hasattr(env, 'notebooks'):
        env.notebooks = {}
    env.notebooks[fromdocname] = to_build


def get_doctree(docname, env):
    dt_fname = pjoin(env.doctreedir, docname + '.doctree')
    with open(dt_fname, 'rb') as fobj:
        content = fobj.read()
    return pickle.loads(content)


def build_notebook(docname):
    return nbf.new_notebook()


def fill_notebook(nb):
    return nb


def write_notebook(nb, filename):
    nb_str = nbf.writes(nb)
    with open(filename, 'wt') as fobj:
        fobj.write(nb_str)


def _relfn2outpath(rel_path, app):
    return pjoin(app.outdir, rel_path)


def write_notebooks(app, exception):
    """ Write notebooks when build has finished """
    if exception is not None:
        return
    env = app.env
    if not hasattr(env, 'notebooks'):
        return
    for docname, to_build in env.notebooks.items():
        doctree = get_doctree(docname, env)
        clear_nb = build_notebook(doctree)
        for rel_fn in to_build.get('clear', []):
            out_fn = _relfn2outpath(rel_fn, app)
            write_notebook(clear_nb, out_fn)
        if not 'full' in to_build:
            continue
        full_nb = fill_notebook(clear_nb)
        for rel_fn in to_build['full']:
            out_fn = _relfn2outpath(rel_fn, app)
            write_notebook(full_nb, out_fn)
    del app.env.notebooks


def visit_notebook_node(self, node):
    self.body.append(
        '<a class="reference download internal" href="{0}">'.format(
            node['filename']))
    self.context.append('</a>')


def depart_notebook_node(self, node):
    self.body.append(self.context.pop())


def setup(app):
    app.add_role('clearnotebook', clearnotebook)
    app.add_role('fullnotebook', fullnotebook)
    app.connect('doctree-resolved', collect_notebooks)
    app.connect('build-finished', write_notebooks)
    app.add_node(notebook_reference,
                 html=(visit_notebook_node, depart_notebook_node))
