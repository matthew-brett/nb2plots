""" Tests for build using nbplot extension """

from os.path import (join as pjoin, dirname, isdir)

from .pagebuilder import setup_module
from .test_proj1 import ModifiedProj1Builder

from nose.tools import assert_true, assert_false

HERE = dirname(__file__)
OTHER_PAGES = pjoin(HERE, 'otherpages')


def file_same(file1, file2):
    with open(file1, 'rb') as fobj:
        contents1 = fobj.read()
    with open(file2, 'rb') as fobj:
        contents2 = fobj.read()
    return contents1 == contents2


class TestNbplots(ModifiedProj1Builder):

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n'
                        'nbplot_include_source = False')
        cls.replace_page(pjoin(OTHER_PAGES, 'some_plots.rst'))

    def test_some_plots(self):
        assert_true(isdir(self.html_dir))

        def plot_file(num):
            return pjoin(self.html_dir, 'a_page-{0}.png'.format(num))

        range_10, range_6, range_4 = [plot_file(i) for i in range(1, 4)]
        # Plot 5 is range(6) plot
        assert_true(file_same(range_6, plot_file(5)))
        # Plot 7 is range(4) plot
        assert_true(file_same(range_4, plot_file(7)))
        # Plot 11 is range(10) plot
        assert_true(file_same(range_10, plot_file(11)))
        # Plot 12 uses the old range(10) figure and the new range(6) figure
        assert_true(file_same(range_10, plot_file('12_00')))
        assert_true(file_same(range_6, plot_file('12_01')))
        # Plot 13 shows close-figs in action
        assert_true(file_same(range_4, plot_file(13)))
        # Plot 13 does not include source
        with open(pjoin(self.html_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_false('# Very unusual comment' in html_contents)
        # Plot 14 has included source
        with open(pjoin(self.html_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_true('# Only a comment' in html_contents)


class TestDefaultSource(ModifiedProj1Builder):
    """ Check that default is to include source """

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::

    # Only a comment
""")

    def test_include_source_default(self):
        # Plot 1 has included source
        with open(pjoin(self.html_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_true('# Only a comment' in html_contents)
