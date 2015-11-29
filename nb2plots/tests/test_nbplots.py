""" Tests for build using nbplot extension """

from os.path import (join as pjoin, dirname, isdir)
from io import StringIO

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
                        'nbplot_include_source = False\n'
                        'nbplot_html_show_source_link = True')
        cls.replace_page(pjoin(OTHER_PAGES, 'some_plots.rst'))

    def test_some_plots(self):
        assert_true(isdir(self.out_dir))

        def plot_file(num):
            return pjoin(self.out_dir, 'a_page-{0}.png'.format(num))

        range_10, range_6, range_4 = [plot_file(i) for i in range(1, 4)]
        # Plot 5 is range(6) plot
        assert_true(file_same(range_6, plot_file(5)))
        # Plot 7 is range(4) plot
        assert_true(file_same(range_4, plot_file(7)))
        # Plot 8 uses the old range(4) figure and the new range(6) figure
        assert_true(file_same(range_4, plot_file('8_00')))
        assert_true(file_same(range_6, plot_file('8_01')))
        # Plot 9 shows the default close-figures behavior in action
        assert_true(file_same(range_4, plot_file(9)))
        # Plot 9 does not include source
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_false('# Very unusual comment' in html_contents)
        # Plot 10 has included source
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_true('# Only a comment' in html_contents)

    def test_html_links_to_source(self):
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html = fobj.read()
        assert_true('href=".//a_page-1.py">Source code</a>' in html)


class TestDefaultSource(ModifiedProj1Builder):
    """ Check that default is to include source, not source links """

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
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_true('# Only a comment' in html_contents)

    def test_no_source_link(self):
        # Plot 1 has included source
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html = fobj.read()
        assert_false('href=".//a_page-1.py">Source code</a>' in html)


class TestAnnoyingParens(ModifiedProj1Builder):
    """ Test we've fixed the empty parens bug

    The matplotlib plotter puts an annoying empty open/close parens in the
    output when html source link is off, and there are no figures.
    """

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n'
                        'nbplot_html_show_source_link = False')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::

    # Only a comment
""")

    def test_annoying_parens(self):
        # Plot 1 has included source
        with open(pjoin(self.out_dir, 'a_page.html'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_false('<p>()</p>' in html_contents)


class TestDefaultContext(ModifiedProj1Builder):
    """ Test that default context is to keep across plots, reset each doc
    """
    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::

    # The namespace reset at the beginning of each document
    assert 'a' not in globals()
    a = 1

Some text.

.. nbplot::

    b = a
    # A plot preserved across nbplot directives
    plt.plot(range(10))

More text.

.. nbplot::
    :keepfigs:

    # This one should result in the same plot as the previous nbplot
    b = b + 3

Yet more text.

.. nbplot::

    # Here, no plot, without the keepfigs directive
    assert b == 4

""")
        cls.add_page(StringIO(u"""\
Another title
-------------

.. nbplot::

    # The namespace reset at the beginning of each document
    assert 'a' not in globals()
    a = 2

Some text.

.. nbplot::

    c = a

"""), 'another_page')

    def test_rebuild_context(self):
        # Does rebuilding still delete context? (Tested in nbplots asserts)
        with open(pjoin(self.page_source, 'another_page.rst'), 'a') as fobj:
            fobj.write('\nSomething added\n')
        with open(pjoin(self.page_source, 'a_page.rst'), 'a') as fobj:
            fobj.write('\nSomething added\n')
        self.__class__.build_source()


class TestRcparams(ModifiedProj1Builder):
    """ Test that rcparams get applied and kept across plots in documents
    """
    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n'
                        'nbplot_rcparams = {"text.color": "red"}\n')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
The start
---------

Plot 1

.. nbplot::

    plt.text(0, 0, "I'm Mr Brightside", color='red')

Plot 2 - shows the default is the same:

.. nbplot::

    plt.text(0, 0, "I'm Mr Brightside")

Plot 3 - changes the default:

.. nbplot::

    plt.rcParams['text.color'] = 'blue'
    plt.text(0, 0, 'Open up my eager eyes')

Plot 4 - new default is blue:

.. nbplot::

    plt.text(0, 0, 'Open up my eager eyes', color='blue')

""")
        cls.add_page(StringIO(u"""
Another title
-------------

Plot color resumes at red:

.. nbplot::

    plt.text(0, 0, "I'm Mr Brightside")

.. nbplot::

    plt.rcParams['text.color'] = 'blue'
    plt.text(0, 0, "Open up my eager eyes")

"""), 'b_page')

    def test_rcparams(self):
        # Test plot rcparams applied at beginning of page

        def gpf(name, num):
            # Get plot file
            return pjoin(self.out_dir, '{0}-{1}.png'.format(name, num))

        red_bright = gpf('a_page', 2)
        blue_eager = gpf('a_page', 4)
        assert_true(file_same(gpf('a_page', 1), red_bright))
        assert_true(file_same(gpf('a_page', 3), blue_eager))
        assert_true(file_same(gpf('b_page', 1), red_bright))


class TestDefaultPre(ModifiedProj1Builder):
    """ Check that default pre code is importing numpy as pyplot

    Tested in plot directive body
    """

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::

    np.inf
    plt.plot(range(10))
""")


class TestNonDefaultPre(ModifiedProj1Builder):
    """ Check that pre code is run in fresh plot context

    Tested in plot directive body
    """

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots"]\n'
                        'nbplot_pre_code = "import numpy as foo; bar = 1"\n')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::

    foo.inf
    assert bar == 1
""")


class TestHiddenDoctests(ModifiedProj1Builder):
    """ Check that doctest code gets hidden but still run

    Build using text builder to get more simply testable output.
    """

    builder = 'text'

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots",'
                        '"sphinx.ext.doctest"]')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::
    :include-source: false

    >>> a = 1
    >>> b = 2

Text1

.. nbplot::

    >>> assert a == 1
    >>> assert b == 2

Text2

.. nbplot::
    :include-source: false

    c = 3

Text3

.. nbplot::

    >>> assert 'c' in globals()
""")

    def test_whats_in_the_page(self):
        with open(pjoin(self.out_dir, 'a_page.txt'), 'rt') as fobj:
            html_contents = fobj.read()
        assert_false('a = 1' in html_contents)
        assert_false('b = 2' in html_contents)
        assert_true('a == 1' in html_contents)
        assert_true('b == 2' in html_contents)
        assert_false('c = 3' in html_contents)


class TestMoreDoctests(ModifiedProj1Builder):
    """ Check that doctest code gets hidden but still tested

    Build using doctest builder
    """

    builder = 'doctest'

    @classmethod
    def modify_source(cls):
        cls.append_conf('extensions = ["nb2plots.nbplots",'
                        '"sphinx.ext.doctest"]')
        with open(pjoin(cls.page_source, 'a_page.rst'), 'wt') as fobj:
            fobj.write("""\
A title
-------

.. nbplot::
    :include-source: false

    >>> a = 1
    >>> b = 2

Text1

.. nbplot::

    >>> a
    1
    >>> b
    2

Text2

.. nbplot::
    :include-source: false

    c = 3

Text3

.. nbplot::

    >>> 'c' not in globals()
    True
""")
