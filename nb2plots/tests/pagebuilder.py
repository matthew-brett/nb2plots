""" Utilities for testing minimal sphinx project builds """

import shutil
import tempfile
import pickle
import re

from os.path import join as pjoin, isdir

from subprocess import call, Popen, PIPE

from nose import SkipTest
from nose.tools import assert_equal


def setup_module():
    try:
        call(['sphinx-build', '--help'], stdout=PIPE, stderr=PIPE)
    except OSError:
        raise SkipTest('Need sphinx-build on PATH for these tests')


def assert_matches(regex, text):
    return re.match(regex, text) is not None


class PageBuilder(object):
    """ Class to build sphinx pages in temporary directory """
    # set to path containing original sources (not modified)
    page_source_template = None

    # If True, assert that the build raised an error
    should_error = False

    @classmethod
    def setup_class(cls):
        cls.build_error = None
        cls.build_path = tempfile.mkdtemp()
        try:  # Catch exceptions during test setup
            cls.set_page_source()  # Sets page_source, maybe modifies source
            cls.html_dir = pjoin(cls.build_path, 'html')
            cls.doctree_dir = pjoin(cls.build_path, 'doctrees')
            # Build the pages with warnings turned into errors
            cmd = ['sphinx-build', '-W', '-b', 'html',
                   '-d', cls.doctree_dir,
                   cls.page_source,
                   cls.html_dir]
        except Exception as e:  # Exceptions during test setup
            shutil.rmtree(cls.build_path)
            raise e
        try:  # Catch exceptions during sphinx build
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            cls.stdout, cls.stderr = proc.communicate()
            if proc.returncode != 0:
                cls.build_error = "Unknown error"
        except Exception as e:  # Exceptions during sphinx build
            cls.build_error = e
        # We will later check if a page build that should error, did error
        if cls.build_error is None or cls.should_error:
            return
        # An unexpected error - delete temp dir and report.
        shutil.rmtree(cls.build_path)
        raise RuntimeError('sphinx-build failed with stdout:\n'
                           '{0}\nstderr:\n{1}\nbuild error {2}'.format(
                               cls.stdout, cls.stderr, cls.build_error))

    @classmethod
    def set_page_source(cls):
        """ Set directory containing page sources

        In simplest case, we don't modify the sources, so the ``page_source``
        is the same as the ``page_source_template``.
        """
        cls.page_source = cls.page_source_template

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


class ModifiedPageBuilder(PageBuilder):
    """ Class to modify sphinx pages in temporary directory before build

    This allows us to make new build configurations and pages in the test
    functions rather than having multiple sphinx project subdirectories in the
    test tree.
    """

    @classmethod
    def set_page_source(cls):
        """ Copy the source to a temporary directory, maybe modify """
        cls.page_source = pjoin(cls.build_path, 'source')
        shutil.copytree(cls.page_source_template, cls.page_source)
        cls.modify_source()

    @classmethod
    def modify_source(cls):
        """ Subclass this class method to modify the build sources """
