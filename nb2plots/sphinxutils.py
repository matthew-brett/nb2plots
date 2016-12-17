""" Utilities for running sphinx tasks in-process
"""

import sys
import os
from os.path import join as pjoin, isdir
import shutil
from contextlib import contextmanager
from copy import copy
from tempfile import mkdtemp
import pickle

from docutils import nodes
from docutils.io import Output

from docutils.parsers.rst import directives, roles

from sphinx.application import Sphinx

fresh_roles = copy(roles._roles)
fresh_directives = copy(directives._directives)
fresh_visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()


def reset_class(cls, original_dict):
    for key in list(cls.__dict__):
        if key not in original_dict:
            delattr(cls, key)
        else:
            setattr(cls, key, original_dict[key])


class TestApp(Sphinx):

    def __init__(self, *args, **kwargs):
        self._set_cache()
        with self.own_namespace():
            super(TestApp, self).__init__(*args, **kwargs)

    def _set_cache(self):
        self._docutils_cache = dict(
            directives=copy(fresh_directives),
            roles=copy(fresh_roles),
            visitor_dict = fresh_visitor_dict)

    @contextmanager
    def own_namespace(self):
        """ Set docutils namespace for builds """
        cache = self._docutils_cache
        _directives = directives._directives
        _roles = roles._roles
        _visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()
        directives._directives = cache['directives']
        roles._roles = cache['roles']
        reset_class(nodes.GenericNodeVisitor, cache['visitor_dict'])
        try:
            yield
        finally:
            directives._directives = _directives
            roles._roles = _roles
            reset_class(nodes.GenericNodeVisitor, _visitor_dict)

    def build(self, *args, **kwargs):
        with self.own_namespace():
            return super(TestApp, self).build(*args, **kwargs)


class TempApp(TestApp):
    """ An application pointing to its own temporary directory.

    The instance deletes its temporary directory when garbage collected.

    Parameters
    ----------
    rst_text : str
        String containing ReST to build.
    conf_text : str, optional
        Text for configuration ``conf.py`` file.
    status : file-like object or None
        File-like object to which to write build status messages, or None for
        no build status messages.
    warningiserror : {True, False}, optional
        If True, raise an error for warning during the Sphinx build.
    """

    def __init__(self, rst_text, conf_text='', buildername='html',
                 status=sys.stdout, warningiserror=True):
        self.tmp_dir = tmp_dir = mkdtemp()
        with open(pjoin(tmp_dir, 'conf.py'), 'wt') as fobj:
            fobj.write(conf_text)
        with open(pjoin(tmp_dir, 'contents.rst'), 'wt') as fobj:
            fobj.write(rst_text)
        self._set_cache()
        with self.own_namespace():
            TestApp.__init__(self,
                             tmp_dir,
                             tmp_dir,
                             tmp_dir,
                             tmp_dir,
                             buildername,
                             status=status,
                             warningiserror=warningiserror)

    def __del__(self):
        shutil.rmtree(self.tmp_dir)


class PageBuilder(object):
    """ Class to build sphinx pages in temporary directory """

    # If True, assert that the build raised an error
    should_error = False

    # Builder
    builder = 'html'

    @classmethod
    def setup_class(cls):
        cls.build_error = None
        cls.build_path = mkdtemp()
        try:  # Catch exceptions during test setup
            # Sets page_source, maybe modifies source
            cls.set_page_source()
            cls.out_dir = pjoin(cls.build_path, cls.builder)
            cls.doctree_dir = pjoin(cls.build_path, 'doctrees')
            # App to build the pages with warnings turned into errors
            cls.build_app = TestApp(
                cls.page_source,
                cls.page_source,
                cls.out_dir,
                cls.doctree_dir,
                cls.builder,
                warningiserror=True)
        except Exception as e:  # Exceptions during test setup
            shutil.rmtree(cls.build_path)
            raise e
        cls.build_source()

    @classmethod
    def build_source(cls):
        try:  # Catch exceptions during sphinx build
            cls.build_app.build(False, [])
            if cls.build_app.statuscode != 0:
                cls.build_error = "Unknown error"
        except Exception as e:  # Exceptions during sphinx build
            cls.build_error = e
        # We will later check if a page build that should error, did error
        if cls.build_error is None or cls.should_error:
            return
        # An unexpected error - delete temp dir and report.
        shutil.rmtree(cls.build_path)
        raise RuntimeError('page build failed with build error {}'
                           .format(cls.build_error))

    @classmethod
    def set_page_source(cls):
        """ Set directory containing page sources
        """
        cls.page_source = pjoin(cls.build_path, 'source')
        os.mkdir(cls.page_source)
        cls.modify_source()

    def get_doctree(self, name):
        """ Return doctree given by `name` from pickle in doctree file """
        with open(pjoin(self.doctree_dir, name + '.doctree'), 'rb') as fobj:
            content = fobj.read()
        return pickle.loads(content)

    @classmethod
    def get_built_file(cls, basename, encoding='utf8'):
        """ Contents of file in build dir with basename `basename`

        Parameters
        ----------
        basename : str
            Basename of file to load, including extension.
        encoding : str, optional
            If None, return contents as bytes.  If not None, decode contents
            with the given encoding.

        Returns
        -------
        content : str or bytes
            Return text contents of file if `encoding` not None, else return
            binary contents of file.
        """
        with open(pjoin(cls.out_dir, basename), 'rb') as fobj:
            content = fobj.read()
        return content if encoding is None else content.decode(encoding)

    def doctree2str(self, doctree):
        """ Return simple string representation from `doctree` """
        return '\n'.join(str(p) for p in doctree.document[0])

    def test_build_error(self):
        # Check whether an expected build error has occurred
        assert self.should_error == (self.build_error is not None)

    @classmethod
    def teardown_class(cls):
        if isdir(cls.build_path):
            shutil.rmtree(cls.build_path)


class SourcesBuilder(PageBuilder):
    """ Build pages with text in class attribute ``rst_sources``.
    """

    rst_sources = dict()
    conf_source = ''

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'conf.py'), 'wt') as fobj:
            fobj.write(cls.conf_source)
        for page_root, page_content in cls.rst_sources.items():
            page_path = pjoin(cls.page_source, page_root + '.rst')
            with open(page_path, 'wt') as fobj:
                fobj.write(page_content)
        # Add pages to toctree to avoid sphinx warning -> error
        indent = ' ' * 4
        page_list = ("\n" + indent).join(cls.rst_sources)
        page_text = "\n\n.. toctree::\n{}:hidden:\n\n{}{}\n\n".format(
                indent,
                indent,
                page_list)
        with open(pjoin(cls.page_source, 'contents.rst'), 'wt') as fobj:
            fobj.write(page_text)


class ModifiedPageBuilder(PageBuilder):
    """ Copy existing pages into temporary directory and modify before build.

    This allows us to make new build configurations and pages in the test
    functions rather than having multiple sphinx project subdirectories in the
    test tree.
    """
    # set to path containing original sources (not modified)
    page_source_template = None

    # Default page.  Should specify a path-less page name that can be replaced
    # in modified builds.
    default_page = None

    @classmethod
    def set_page_source(cls):
        """ Copy the source to a temporary directory, maybe modify """
        cls.page_source = pjoin(cls.build_path, 'source')
        shutil.copytree(cls.page_source_template, cls.page_source)
        cls.modify_source()

    @classmethod
    def modify_source(cls):
        """ Subclass this class method to modify the build sources """

    @classmethod
    def append_conf(cls, string):
        """ Append stuff to the conf.py file """
        with open(pjoin(cls.page_source, 'conf.py'), 'a') as fobj:
            fobj.write(string)

    @classmethod
    def replace_page(cls, file_like):
        """ Replace default page with contents of `file_like`
        """
        out_fname = pjoin(cls.page_source, cls.default_page)
        if hasattr(file_like, 'read'):
            contents = file_like.read()
            with open(out_fname, 'wt') as fobj:
                fobj.write(contents)
            return
        shutil.copyfile(file_like, out_fname)

    @classmethod
    def add_page(cls, file_like, out_name):
        """ Add another page from `file_like` with name `out_name`
        """
        out_fname = pjoin(cls.page_source, out_name + '.rst')
        if hasattr(file_like, 'read'):
            contents = file_like.read()
            with open(out_fname, 'wt') as fobj:
                fobj.write(contents)
        else:
            shutil.copyfile(file_like, out_fname)
        with open(pjoin(cls.page_source, 'index.rst'), 'a') as fobj:
            fobj.write("\n\n.. toctree::\n\n    {0}\n\n".format(out_name))


class UnicodeOutput(Output):
    """ Don't do anything to the string; just return it.
    """

    default_destination_path = '<string>'

    def write(self, data):
        """ Store `data` in `self.destination`, and return it."""
        self.destination = data
        return data


class Converter(object):
    """ Class to convert from ReST or doctree to output format
    """

    default_conf = ''

    def __init__(self, writer_class, conf_txt=None):
        self.writer_class = writer_class
        self.conf_txt = conf_txt if not conf_txt is None else self.default_conf

    def build_rst(self, rst_text, status=sys.stdout, warningiserror=True):
        """ Build ReST text in string `rst_text` into doctree.

        Parameters
        ----------
        rst_text : str
            string containing ReST to build.
        status : file-like object or None
            File-like object to which to write build status messages, or None
            for no build status messages.
        warningiserror : {True, False}, optional
            if True, raise an error for warning during the Sphinx build.

        Returns
        -------
        doctree : node
            document node.
        """
        app = TempApp(rst_text, self.conf_txt, status=status,
                      warningiserror=warningiserror)
        app.build(False, [])
        return app.env.get_doctree('contents')

    def from_doctree(self, doctree):
        """ Convert doctree `doctree` to output format

        Parameters
        ----------
        doctree : node
            Document node.

        Returns
        ------
        output : str
            Representation in output format
        """
        return self.writer_class().write(doctree, UnicodeOutput())

    def from_rst(self, rst_text,
                 status=sys.stdout,
                 warningiserror=True):
        """ Build Sphinx formatted ReST text `rst_text` into output format

        Parameters
        ----------
        rst_text : str
            string containing ReST to build.
        conf_txt : None or str, optional
            text for configuration ``conf.py`` file.  None gives a default conf
            file.
        status : file-like object or None
            File-like object to which to write build status messages, or None
            for no build status messages.
        warningiserror : {True, False}, optional
            if True, raise an error for warning during the Sphinx build.

        Returns
        -------
        output : str
            Text in output format
        """
        doctree = self.build_rst(rst_text, status=status,
                                 warningiserror=warningiserror)
        return self.writer_class().write(doctree, UnicodeOutput())
