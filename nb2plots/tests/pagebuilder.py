""" Utilities for testing minimal sphinx project builds """

import shutil
import tempfile
import pickle
import re

from os.path import join as pjoin

from subprocess import call, Popen, PIPE

from nose import SkipTest


def setup_module():
    try:
        call(['sphinx-build', '--help'], stdout=PIPE, stderr=PIPE)
    except OSError:
        raise SkipTest('Need sphinx-build on PATH for these tests')


def assert_matches(regex, text):
    return re.match(regex, text) is not None


class PageBuilder(object):
    """ Class to build sphinx pages in temporary directory """
    page_path = None

    @classmethod
    def setup_class(cls):
        cls.page_build = tempfile.mkdtemp()
        try:
            cls.html_dir = pjoin(cls.page_build, 'html')
            cls.doctree_dir = pjoin(cls.page_build, 'doctrees')
            # Build the pages with warnings turned into errors
            cmd = ['sphinx-build', '-W', '-b', 'html',
                   '-d', cls.doctree_dir,
                   cls.page_path,
                   cls.html_dir]
            proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
            out, err = proc.communicate()
        except Exception as e:
            shutil.rmtree(cls.page_build)
            raise e
        if proc.returncode != 0:
            shutil.rmtree(cls.page_build)
            raise RuntimeError('sphinx-build failed with stdout:\n'
                               '{0}\nstderr:\n{1}\n'.format(
                                    out, err))

    def get_doctree(self, name):
        with open(pjoin(self.doctree_dir, name + '.doctree'), 'rb') as fobj:
            content = fobj.read()
        return pickle.loads(content)

    def doctree2str(self, doctree):
        return '\n'.join(str(p) for p in doctree.document[0])

    @classmethod
    def teardown_class(cls):
        shutil.rmtree(cls.page_build)
