""" Tests for proj1 build using sphinx extensions """

from os.path import (join as pjoin, dirname, isdir, exists)

from .pagebuilder import setup_module, PageBuilder, ModifiedPageBuilder

from nose.tools import assert_true, assert_equal

HERE = dirname(__file__)
PAGES = pjoin(HERE, 'proj1')

PAGE_HEADER = """\
A title
=======

"""

class Proj1Builder(PageBuilder):
    page_source_template = PAGES


class TestProj1(Proj1Builder):

    def test_basic_build(self):
        assert_true(isdir(self.out_dir))
        assert_true(isdir(self.doctree_dir))
        doctree = self.get_doctree('a_page')
        assert_equal(len(doctree.document), 1)
        doctree_str = self.doctree2str(doctree)
        assert_equal(
            doctree_str,
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph><notebook_reference evaluate="False" '
            'refdoc="a_page" reftarget="a_page.ipynb" reftype="clearnotebook">'
            'notebook here</notebook_reference></paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph><notebook_reference evaluate="True" '
            'refdoc="a_page" reftarget="another.ipynb" reftype="fullnotebook">'
            'full</notebook_reference></paragraph>')
        assert_true(exists(pjoin(self.build_path, 'html', 'a_page.ipynb')))


class ModifiedProj1Builder(ModifiedPageBuilder):
    page_source_template = PAGES
    default_page = 'a_page.rst'


class TestNotSameName(ModifiedProj1Builder):

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write(PAGE_HEADER +
"""
:clearnotebook:`.` (the default name and text).

:fullnotebook:`Get it here <another_name.ipynb>` (not-default name).
""")


class TestSameName(ModifiedPageBuilder):
    page_source_template = PAGES
    should_error = True

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write(PAGE_HEADER +
"""
:clearnotebook:`.` (the default name).

:fullnotebook:`.` (default name again).
""")
