""" Sphinx extension to convert RST pages to notebooks """

from os.path import join as pjoin
from copy import deepcopy

from docutils import nodes, utils
from docutils.parsers.rst import directives
from docutils.parsers.rst.roles import set_classes

from sphinx.util.nodes import split_explicit_title, set_role_source_info
from sphinx.errors import ExtensionError

# Use notebook format version 4
from .ipython_shim import nbf, nbconvert as nbc

from . import doctree2nb, doctree2py
from .converters import to_notebook

from nb2plots.nbplots import drop_visit


class RunRoleError(ExtensionError):
    """ Error for runnable role Sphinx extensions """


class runrole_reference(nodes.reference):
    """Node for references to built runnable, similar to pending_xref."""


class ClearNotebookRunRole(object):
    """ Role builder for not-evaluated notebook """

    evaluate = False
    default_text = 'Download this page as a Jupyter notebook'
    default_extension = '.ipynb'

    def __call__(self, name, rawtext, text, lineno, inliner, options={},
                    content=[]):
        """ Role for building and linking to built code files

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
        set_classes(options)
        # Get objects from context
        env = inliner.document.settings.env
        # Get title and link
        text = utils.unescape(text)
        text = self.default_text if text.strip() == '.' else text
        has_fname, title, fname = split_explicit_title(text)
        if not has_fname:
            fname = env.docname + self.default_extension
        refnode = runrole_reference(rawtext, title, reftype=name)
        # We may need the line number for warnings
        set_role_source_info(inliner, lineno, refnode)
        refnode['reftarget'] = fname
        # we also need the source document
        refnode['refdoc'] = env.docname
        refnode['evaluate'] = self.evaluate
        # result_nodes allow further modification of return values
        return [refnode], []


class FullNotebookRunRole(ClearNotebookRunRole):
    """ Role builder for evaluated notebook """

    evaluate = True


clearnotebook = ClearNotebookRunRole()
fullnotebook = FullNotebookRunRole()


def collect_notebooks(app, doctree, fromdocname):
    env = app.env
    out_notebooks = {}
    for nb_ref in doctree.traverse(runrole_reference):
        # Calculate relative filename
        rel_fn, _  = env.relfn2path(nb_ref['reftarget'], fromdocname)
        # Check for duplicates
        evaluate = nb_ref['evaluate']
        if rel_fn not in out_notebooks:
            out_notebooks[rel_fn] = evaluate
        elif out_notebooks[rel_fn] != evaluate:
            raise RunRoleError('Notebook filename {0} cannot be both '
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


def fill_notebook(nb):
    """ Execute notebook `nb` and return notebook with built outputs
    """
    preprocessor = nbc.preprocessors.execute.ExecutePreprocessor()
    preprocessor.enabled = True
    res = nbc.exporter.ResourcesDict()
    res['metadata'] = nbc.exporter.ResourcesDict()
    output_nb, _ = preprocessor(deepcopy(nb), res)
    return output_nb


def write_notebook(nb, filename):
    """ Write notebook `nb` to filename `filename`
    """
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
        doctree = app.env.get_doctree(docname)
        clear_nb = nbf.reads(to_notebook.from_doctree(doctree))
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


def visit_runrole(self, node):
    self.body.append(
        '<a class="reference download internal" href="{0}">'.format(
            node['filename']))
    self.context.append('</a>')


def depart_runrole(self, node):
    self.body.append(self.context.pop())


def setup(app):
    app.add_role('clearnotebook', clearnotebook)
    app.add_role('fullnotebook', fullnotebook)
    app.connect('doctree-resolved', collect_notebooks)
    app.connect('build-finished', write_notebooks)
    app.add_node(runrole_reference,
                 html=(visit_runrole, depart_runrole),
                 text=(drop_visit, None),
                 latex=(drop_visit, None))
    # Register translators to allow other extensions to extend ipynb and python
    # code visit, depart methods with app.add_node as we have just done for the
    # html translator in the lines above.  See:
    # http://www.sphinx-doc.org/en/1.4.8/extdev/tutorial.html#the-setup-function
    app.set_translator('ipynb', doctree2nb.Translator)
    app.set_translator('python', doctree2py.Translator)
