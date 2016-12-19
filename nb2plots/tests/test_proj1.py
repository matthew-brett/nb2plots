""" Tests for proj1 build using sphinx extensions """

from os.path import (join as pjoin, dirname, isdir, exists)

from nb2plots.sphinxutils import ModifiedPageBuilder

from nose.tools import assert_true, assert_equal

HERE = dirname(__file__)

PAGE_HEADER = """\
A title
=======

"""

class Proj1Builder(ModifiedPageBuilder):
    """ Build using 'proj1' directory as template to modify
    """

    page_source_template = pjoin(HERE, 'proj1')

    # default_page used in 'replace_page' class method
    default_page = 'a_page.rst'


class TestProj1(Proj1Builder):

    def test_basic_build(self):
        assert_true(isdir(self.out_dir))
        assert_true(isdir(self.doctree_dir))
        doctree = self.get_doctree('a_page')
        assert_equal(len(doctree.document), 1)
        doctree_str = self.doctree2str(doctree)
        expected = (
            '<title>A section</title>\n'
            '<paragraph>Some text.</paragraph>\n'
            '<paragraph><runrole_reference code_type="clear notebook" '
            'refdoc="a_page" reftarget="a_page.ipynb" reftype="clearnotebook">'
            'notebook here</runrole_reference></paragraph>\n'
            '<paragraph>More text.</paragraph>\n'
            '<paragraph><runrole_reference code_type="full notebook" '
            'refdoc="a_page" reftarget="another.ipynb" reftype="fullnotebook">'
            'full</runrole_reference></paragraph>\n'
            '<paragraph>Text is endless.</paragraph>\n'
            '<paragraph><runrole_reference code_type="python" '
            'refdoc="a_page" reftarget="a_page.py" reftype="codefile">'
            'code here</runrole_reference></paragraph>')
        assert_equal(doctree_str, expected)
        # Check the expected files were written
        for fname in ('a_page.ipynb', 'another.ipynb', 'a_page.py'):
            built_fname = pjoin(self.build_path, 'html', fname)
            assert_true(exists(built_fname))


class TestNotSameName(Proj1Builder):

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write(PAGE_HEADER +
"""
:clearnotebook:`.` (the default name and text).

:fullnotebook:`Get it here <another_name.ipynb>` (not-default name).
""")


class TestSameNameIpy(Proj1Builder):
    should_error = True

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write(PAGE_HEADER +
"""
:clearnotebook:`.` (the default name).

:fullnotebook:`.` (default name again).
""")

class TestSameNamePy(Proj1Builder):
    should_error = True

    @classmethod
    def modify_source(cls):
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write(PAGE_HEADER +
"""
:clearnotebook:`.` (the default name).

:codefile:`code file <a_page.ipynb>` (same name as notebook)
""")
