""" Tests for proj1 build using sphinx extensions """

from os.path import (join as pjoin, dirname, isdir)

from .pagebuilder import setup_module, PageBuilder

from nose.tools import assert_true, assert_equal

HERE = dirname(__file__)
PAGES = pjoin(HERE, 'proj1')


class TestProj1(PageBuilder):
    # Test build and output of tinypages project
    page_path = PAGES

    def test_some_math(self):
        assert_true(isdir(self.html_dir))
        assert_true(isdir(self.doctree_dir))
        doctree = self.get_doctree('a_page')
        assert_equal(len(doctree.document), 1)
        doctree_str = self.doctree2str(doctree)
        assert_equal(doctree_str,
                     '<title>A section</title>\n'
                     '<paragraph>Some text</paragraph>')
