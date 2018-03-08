""" Sphinx extension to convert RST pages to notebooks """

from os import makedirs
from os.path import join as pjoin, dirname, isdir
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
from .converters import UnicodeOutput


class RunRoleError(ExtensionError):
    """ Error for runnable role Sphinx extensions """


class runrole_reference(nodes.reference):
    """Node for references to built runnable, similar to pending_xref."""


class PyRunRole(object):
    """ Role builder for Python code file """

    default_text = 'Download this page as a Python code file'
    default_extension = '.py'
    code_type = 'pyfile'
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
        # Get objects from context
        env = inliner.document.settings.env
        # process class options.
        # http://docutils.sourceforge.net/docs/howto/rst-roles.html
        # Remaining options will be added as attributes of the node (see
        # below).
        set_classes(options)
        # Get title and link
        text = utils.unescape(text)
        text = self.default_text if text.strip() == '.' else text
        has_fname, title, fname = split_explicit_title(text)
        if not has_fname:
            fname = '/' + env.docname + self.default_extension
        refnode = runrole_reference(rawtext, title,
                                    reftype=self.code_type,
                                    refdoc=env.docname,
                                    reftarget=fname,
                                    **options)
        # We may need the line number for warnings
        set_role_source_info(inliner, lineno, refnode)
        return [refnode], []

    def write_queue(self, queue, app):
        """ Write queue of runnable nodes

        Parameters
        ----------
        queue : iterable
            Iterable of Docutils nodes, where the nodes specify runnable
            builds, including (for each node) the filename of original ReST
            document.
        app : Sphinx Application
            Application responsible for build.
        """
        for node in queue:
            self.write(node, app)

    def write(self, node, app):
        """ Build + cache runnable, or return build from cache.

        Parameters
        ----------
        node : docutils node
            Docutils node specifying runnable build, including filename of
            original ReST document.
        app : Sphinx Application
            Application responsible for build.
        """
        out_fname = _relfn2outpath(node['filename'], app)
        built = self.get_built(node, app)
        path = dirname(out_fname)
        if not isdir(path):
            makedirs(path)
        with open(out_fname, 'wb') as fobj:
            fobj.write(built.encode(self.encoding))

    def get_built(self, node, app):
        """ Build, cache, return output object, or return from cache.

        Parameters
        ----------
        node : object
            Runrole node.
        app : object
            Sphinx application in charge of build

        Returns
        -------
        output : built output.
        """
        code_type = self.code_type
        own_params = app.env.runrole_cache[node['refdoc']]
        if own_params.get(code_type) is None:
            own_params[code_type] = self._build(node, app)
        return own_params[code_type]

    def _build(self, node, app):
        """ Return string containing built / resolved version of `doctree`
        """
        builder = self.builder_class(app)
        docname = node['refdoc']
        doctree = app.env.get_and_resolve_doctree(docname, builder)
        builder.prepare_writing([docname])
        # Set current docname for writer to work out link targets
        builder.current_docname = docname
        return builder.writer.write(doctree, UnicodeOutput())


class ClearNotebookRunRole(PyRunRole):
    """ Role builder for not-evaluated notebook """

    default_text = 'Download this page as a Jupyter notebook (no outputs)'
    default_extension = '.ipynb'
    code_type = 'clearnotebook'
    builder_class = NotebookBuilder


def convert_timeout(argument):
    """ Allow -1, 0, positive integers and None

    These are the valid options for the nbconvert timeout option.
    """
    if argument.lower() == 'none':
        return None
    value = int(argument)
    if value < -1:
        raise ValueError('Value less than -1 not allowed')
    return value


class FullNotebookRunRole(ClearNotebookRunRole):
    """ Role builder for evaluated notebook """

    default_text = 'Download this page as a Jupyter notebook (with outputs)'
    code_type = 'fullnotebook'

    options = dict(timeout=convert_timeout)

    def __init__(self, clear_role):
        self.clear_role = clear_role

    def write_queue(self, queue, app):
        """ Write queue of runnable nodes

        Choose longest timeout for duplicate builds.

        Parameters
        ----------
        queue : iterable
            Iterable of Docutils nodes, where the nodes specify runnable
            builds, including (for each node) the filename of original ReST
            document.
        app : Sphinx Application
            Application responsible for build.
        """
        # Set longest timeout to duplicates
        for docname in set(n['refdoc'] for n in queue):
            duplicates = [n for n in queue if n['refdoc'] == docname]
            timeouts = set(n['timeout'] for n in duplicates if 'timeout' in n)
            if len(timeouts) < 2:
                continue
            max_timeout = (-1 if {None, -1}.intersection(timeouts)
                           else max(timeouts))
            for n in duplicates:
                n['timeout'] = max_timeout

        for node in queue:
            self.write(node, app)

    def _build(self, node, env):
        """ Return byte string containing built version of `doctree` """
        empty_json = self.clear_role.get_built(node, env)
        timeout = node.get('timeout', env.config.fill_notebook_timeout)
        full_nb = fill_notebook(nbf.reads(empty_json), timeout=timeout)
        return nbf.writes(full_nb)


# Collect instances of the known role types
_clearnotebook = ClearNotebookRunRole()
NAME2ROLE = dict(pyfile=PyRunRole(),
                 codefile=PyRunRole(),  # compatibility with older name
                 clearnotebook=_clearnotebook,
                 fullnotebook=FullNotebookRunRole(_clearnotebook))


def do_builder_init(app):
    """ Initialize builder with empty runrole caches and queues.
    """
    env = app.env
    env.runrole_queue = defaultdict(list)
    env.runrole_cache = defaultdict(dict)


def do_purge_doc(app, env, docname):
    """ Clear caches and queues of runrole builds from this `docname`.
    """
    env.runrole_cache.pop(docname, None)
    queues = env.runrole_queue
    for code_type in queues:
        queues[code_type] = [node for node in queues[code_type]
                             if node['refdoc'] != docname]


def collect_runfiles(app, doctree, fromdocname):
    r""" Collate requested runnable files, store in env

    Traverse doctree, find runrole nodes, and collect the nodes that need to be
    built.  Store references to the nodes in the ``env.runroles_queue``
    dictionary, The dictionary has keys giving runrole type (string, one
    of 'pyfile', 'clearnotebook', 'fullnotebook') and values that are lists
    of nodes to be built into runnable outputs.

    Set filename of file to be built into node.

    Called at ``doctree-resolved`` event.
    """
    env = app.env
    queues = env.runrole_queue
    files = {}

    for ref in doctree.traverse(runrole_reference):
        # Calculate filename of file to be built, relative to project root
        rel_fn, _ = env.relfn2path(ref['reftarget'], ref['refdoc'])
        ref['filename'] = rel_fn
        # Check for duplicates.  It's OK to reference a file that is already
        # registered for building, but it must be of the same code type.
        code_type = ref['reftype']
        if rel_fn not in files:
            files[rel_fn] = code_type
        elif files[rel_fn] != code_type:
            raise RunRoleError(
                'Trying to register filename {0} as type {1}, '
                'but it is already registered as type {2}'.format(
                    rel_fn,
                    code_type,
                    files[rel_fn]))
        # The queue can have duplicate combinations of (docname, code_type,
        # rel_fn).
        queues[code_type].append(ref)


def _relfn2outpath(rel_path, app):
    return pjoin(app.outdir, rel_path)


def write_runfiles(app, exception):
    """ Write notebooks / code files when build has finished

    :func:`collect_runfiles` has already collected the files that need to be
    built, and stored then in the ``env.runroles`` dictionary.  See the
    docstring for that function for details.

    We cycle through these collected relative filenames, and build the
    necessary files using the ``write`` method of the stored role instances.

    Called at ``build-finished`` event.
    """
    if exception is not None:
        return
    for code_type, queue in app.env.runrole_queue.items():
        NAME2ROLE[code_type].write_queue(queue, app)


def visit_runrole(self, node):
    self.body.append(
        '<a class="reference download internal" href="{0}">'.format(
            node['filename']))
    self.context.append('</a>')


def depart_runrole(self, node):
    self.body.append(self.context.pop())


def fill_notebook(nb, timeout=30):
    """ Execute notebook `nb` and return notebook with built outputs
    """
    preprocessor = nbc.preprocessors.execute.ExecutePreprocessor(
        timeout=timeout)
    preprocessor.enabled = True
    res = nbc.exporter.ResourcesDict()
    res['metadata'] = nbc.exporter.ResourcesDict()
    output_nb, _ = preprocessor(deepcopy(nb), res)
    return output_nb


def drop_visit(self, node):
    raise nodes.SkipNode


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
    app.set_translator('markdown', doctree2py.Translator)
    app.set_translator('pyfile', doctree2py.Translator)
    app.set_translator('ipynb', doctree2nb.Translator)
