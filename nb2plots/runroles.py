""" Sphinx extension to convert RST pages to notebooks """

from os.path import join as pjoin
from copy import deepcopy
from collections import defaultdict

from docutils import nodes, utils
from docutils.parsers.rst.roles import set_classes

from sphinx.util.nodes import split_explicit_title, set_role_source_info
from sphinx.errors import ExtensionError

# Use notebook format version 4
from .ipython_shim import nbf, nbconvert as nbc

from . import doctree2nb, doctree2py
from .sphinx2foos import PythonBuilder, NotebookBuilder
from .sphinxutils import UnicodeOutput


from nb2plots.nbplots import drop_visit


class RunRoleError(ExtensionError):
    """ Error for runnable role Sphinx extensions """


class runrole_reference(nodes.reference):
    """Node for references to built runnable, similar to pending_xref."""


class PyRunRole(object):
    """ Role builder for Python code file """

    default_text = 'Download this page as a Python code file'
    default_extension = '.py'
    code_type = 'python'
    builder_class = PythonBuilder
    encoding = 'utf-8'

    _cache = {}

    def __call__(self, name, rawtext, text, lineno, inliner, options={},
                 content=[]):
        """ Register this document for later building as runnable code file.

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
        # result_nodes allow further modification of return values
        refnode['code_type'] = self.code_type
        return [refnode], []

    def write(self, docname, app, out_fname):
        built = self.get_built(docname, app)
        with open(out_fname, 'wb') as fobj:
            fobj.write(built.encode(self.encoding))

    def get_built(self, docname, app):
        """ Build, cache output file

        Parameters
        ----------
        docname : str
            Document name.
        app : object
            Sphinx application in charge of build
        """
        own_params = app.env.runrole[docname][self.code_type]
        if own_params['built'] is None:
            own_params['built'] = self._build(docname, app)
        return own_params['built']

    def _build(self, docname, app):
        """ Return string containing built / resolved version of `doctree`
        """
        builder = self.builder_class(app)
        doctree = app.env.get_and_resolve_doctree(docname, builder)
        builder.prepare_writing([docname])
        # Set current docname for writer to work out link targets
        builder.current_docname = docname
        return builder.writer.write(doctree, UnicodeOutput())

    def clear_cache(self, docname, env):
        env.runrole[docname][self.code_type]['built'] = None


class ClearNotebookRunRole(PyRunRole):
    """ Role builder for not-evaluated notebook """

    default_text = 'Download this page as a Jupyter notebook (no outputs)'
    default_extension = '.ipynb'
    code_type = 'clear notebook'
    builder_class = NotebookBuilder


class FullNotebookRunRole(ClearNotebookRunRole):
    """ Role builder for evaluated notebook """

    default_text = 'Download this page as a Jupyter notebook (with outputs)'
    code_type = 'full notebook'

    def __init__(self, clear_role):
        self.clear_role = clear_role

    def _build(self, docname, env):
        """ Return byte string containing built version of `doctree` """
        empty_json = self.clear_role.get_built(docname, env)
        full_nb = fill_notebook(nbf.reads(empty_json))
        return nbf.writes(full_nb)


_clearnotebook = ClearNotebookRunRole()
NAME2ROLE = dict(codefile=PyRunRole(),
                 clearnotebook=_clearnotebook,
                 fullnotebook=FullNotebookRunRole(_clearnotebook))

_TYPE2ROLE = {role.code_type: role for role in NAME2ROLE.values()}


def _empty_rundict():
    return {code_type: dict(to_build=[], built=None)
            for code_type in _TYPE2ROLE}


def do_builder_init(app):
    """ Initialize builder with runrole caches
    """
    env = app.env
    env.runrole = defaultdict(_empty_rundict)


def do_purge_doc(app, env, docname):
    """ Clear caches of runrole builds and finds
    """
    env.runrole[docname] = _empty_rundict()


def collect_runfiles(app, doctree, fromdocname):
    env = app.env
    out_files = {}
    for ref in doctree.traverse(runrole_reference):
        # Calculate relative filename
        rel_fn, _ = env.relfn2path(ref['reftarget'], fromdocname)
        # Check for duplicates
        code_type = ref['code_type']
        if rel_fn not in out_files:
            out_files[rel_fn] = code_type
        elif out_files[rel_fn] != code_type:
            raise RunRoleError(
                'Trying to register filename {0} as {1}, '
                'but it is already registered as {2}'.format(
                    rel_fn, code_type, out_files[rel_fn]))
        ref['filename'] = rel_fn
    if len(out_files) == 0:
        return
    own_params = env.runrole[fromdocname]
    for rel_fn, code_type in out_files.items():
        own_params[code_type]['to_build'].append(rel_fn)


def _relfn2outpath(rel_path, app):
    return pjoin(app.outdir, rel_path)


def write_runfiles(app, exception):
    """ Write notebooks / code files when build has finished """
    if exception is not None:
        return
    env = app.env
    for docname, type_params in env.runrole.items():
        for code_type, build_params in type_params.items():
            role = _TYPE2ROLE[code_type]
            for rel_fname in build_params['to_build']:
                out_fname = _relfn2outpath(rel_fname, app)
                role.write(docname, app, out_fname)
        for role in _TYPE2ROLE.values():
            role.clear_cache(docname, env)


def visit_runrole(self, node):
    self.body.append(
        '<a class="reference download internal" href="{0}">'.format(
            node['filename']))
    self.context.append('</a>')


def depart_runrole(self, node):
    self.body.append(self.context.pop())


def fill_notebook(nb):
    """ Execute notebook `nb` and return notebook with built outputs
    """
    preprocessor = nbc.preprocessors.execute.ExecutePreprocessor()
    preprocessor.enabled = True
    res = nbc.exporter.ResourcesDict()
    res['metadata'] = nbc.exporter.ResourcesDict()
    output_nb, _ = preprocessor(deepcopy(nb), res)
    return output_nb


def setup(app):
    # Add runrole roles
    for name, role in NAME2ROLE.items():
        app.add_role(name, role)
    # Create dictionaries in builder environment
    app.connect(str('builder-inited'), do_builder_init)
    # Delete caches when document re-initialized
    app.connect('env-purge-doc', do_purge_doc)
    # Collect and check all runrole nodes when doctree done
    app.connect('doctree-resolved', collect_runfiles)
    # Write output files at end of build
    app.connect('build-finished', write_runfiles)
    app.add_node(runrole_reference,
                 html=(visit_runrole, depart_runrole),
                 text=(drop_visit, None),
                 latex=(drop_visit, None))
    # Register translators to allow other extensions to extend ipynb and python
    # code visit, depart methods with app.add_node as we have just done for the
    # html translator in the lines above.  See:
    # http://www.sphinx-doc.org/en/1.4.8/extdev/tutorial.html#the-setup-function
    app.set_translator('python', doctree2py.Translator)
    app.set_translator('ipynb', doctree2nb.Translator)
