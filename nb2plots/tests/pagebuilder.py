""" Utilities for testing minimal sphinx project builds """

import shutil
import tempfile
import pickle
import re
import os
from os.path import join as pjoin, isdir

from nb2plots.sphinxutils import TestApp

from nose.tools import assert_equal

def assert_matches(regex, text):
    return re.match(regex, text) is not None


class PageBuilder(object):
    """ Class to build sphinx pages in temporary directory """

    # If True, assert that the build raised an error
    should_error = False

    # Builder
    builder = 'html'

    @classmethod
    def setup_class(cls):
        cls.build_error = None
        cls.build_path = tempfile.mkdtemp()
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

    def doctree2str(self, doctree):
        """ Return simple string representation from `doctree` """
        return '\n'.join(str(p) for p in doctree.document[0])

    def test_build_error(self):
        # Check whether an expected build error has occurred
        assert_equal(self.should_error, self.build_error is not None)

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
            with open(pjoin(cls.page_source, page_root + '.rst'), 'wt') as fobj:
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
    """ Modify existing sphinx pages in temporary directory before build

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
