""" Tests for build using nbplot extension """

from os.path import (join as pjoin, dirname, isdir)
import re

from nb2plots.nbplots import run_code, parse_parts
from nb2plots.sphinxutils import SourcesBuilder

from nose.tools import (assert_true, assert_false, assert_equal, assert_raises)

HERE = dirname(__file__)


def get_otherpage(fname):
    with open(pjoin(HERE, 'otherpages', fname), 'rt') as fobj:
        return fobj.read()


def file_same(file1, file2):
    with open(file1, 'rb') as fobj:
        contents1 = fobj.read()
    with open(file2, 'rb') as fobj:
        contents2 = fobj.read()
    return contents1 == contents2


def test_run_code():
    # Test run_code function
    ns1 = run_code('a = 10')
    assert_equal(ns1['a'], 10)
    assert_false('b' in ns1)
    # New namespace by default
    ns2 = run_code('b = 20')
    assert_equal(ns2['b'], 20)
    assert_false('a' in ns2)
    # Adding to a namespace
    ns3 = run_code('c = 30', ns=ns1)
    assert_true(ns3 is ns1)
    assert_equal(ns1['c'], 30)
    # Checking raises
    run_code('d', raises=NameError)


class TestNbplots(SourcesBuilder):

    conf_source = ('extensions = ["nb2plots.nbplots"]\n'
                   'nbplot_include_source = False\n'
                   'nbplot_html_show_source_link = True')

    rst_sources = dict(a_page=get_otherpage('some_plots.rst'))

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
        html_contents = self.get_built_file('a_page.html')
        # Plot 10 has included source
        assert_true('# Only a comment' in html_contents)
        # HTML links to source
        assert_true('href=".//a_page-1.py">Source code</a>' in html_contents)


class PlotsBuilder(SourcesBuilder):
    """ Build pages with nbplots default extensions
    """

    conf_source = 'extensions = ["nb2plots.nbplots", "sphinx.ext.doctest"]'


class TestDefaultSource(PlotsBuilder):
    """ Check that default is to include source, not source links """

    rst_sources = dict(a_page="""\
A title
-------

.. nbplot::

    # Only a comment
""")

    def test_include_source_default(self):
        # Plot 1 has included source
        html_contents = self.get_built_file('a_page.html')
        assert_true('# Only a comment' in html_contents)
        # Plot 1 has no source link
        html_contents = self.get_built_file('a_page.html')
        assert_false('href=".//a_page-1.py">Source code</a>' in html_contents)


class TestAnnoyingParens(PlotsBuilder):
    """ Test we've fixed the empty parens bug

    The matplotlib plotter puts an annoying empty open/close parens in the
    output when html source link is off, and there are no figures.
    """

    conf_source = ('extensions = ["nb2plots.nbplots"]\n'
                   'nbplot_html_show_source_link = False')

    rst_sources = dict(a_page="""\
A title
-------

.. nbplot::

    # Only a comment
""")

    def test_annoying_parens(self):
        # Plot 1 has included source
        assert_false('<p>()</p>' in self.get_built_file('a_page.html'))


class TestDefaultContext(PlotsBuilder):
    """ Test that default context is to keep across plots, reset each doc
    """

    rst_sources = dict(a_page="""\
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

""",

                      another_page="""\
Another title
-------------

.. nbplot::

    # The namespace reset at the beginning of each document
    assert 'a' not in globals()
    a = 2

Some text.

.. nbplot::

    c = a

""")

    def test_rebuild_context(self):
        # Does rebuilding still delete context? (Tested in nbplots asserts)
        with open(pjoin(self.page_source, 'another_page.rst'), 'a') as fobj:
            fobj.write('\nSomething added\n')
        with open(pjoin(self.page_source, 'a_page.rst'), 'a') as fobj:
            fobj.write('\nSomething added\n')
        self.__class__.build_source()


class TestRcparams(PlotsBuilder):
    """ Test that rcparams get applied and kept across plots in documents
    """
    conf_source = ('extensions = ["nb2plots.nbplots"]\n'
                   'nbplot_rcparams = {"text.color": "red"}\n')
    rst_sources = dict(a_page="""\
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

""",
                       b_page="""
Another title
-------------

Plot color resumes at red:

.. nbplot::

    plt.text(0, 0, "I'm Mr Brightside")

.. nbplot::

    plt.rcParams['text.color'] = 'blue'
    plt.text(0, 0, "Open up my eager eyes")

""")

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


class TestDefaultPre(PlotsBuilder):
    """ Check that default pre code is importing numpy as pyplot

    Tested in plot directive body
    """

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::

    np.inf
    plt.plot(range(10))
""")


class TestNonDefaultPre(PlotsBuilder):
    """ Check that pre code is run in fresh plot context

    Tested in plot directive body
    """
    conf_source=('extensions = ["nb2plots.nbplots"]\n'
                 'nbplot_pre_code = "import numpy as foo; bar = 1"\n')
    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::

    foo.inf
    assert bar == 1
""")


class TestHiddenDoctests(PlotsBuilder):
    """ Check that doctest code gets hidden but still run

    Build using text builder to get more simply testable output.
    """

    builder = 'text'

    rst_sources=dict(a_page="""\
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
        txt_contents = self.get_built_file('a_page.txt')
        assert_false('a = 1' in txt_contents)
        assert_false('b = 2' in txt_contents)
        assert_true('a == 1' in txt_contents)
        assert_true('b == 2' in txt_contents)
        assert_false('c = 3' in txt_contents)


class TestMoreDoctests(PlotsBuilder):
    """ Check that doctest code gets hidden but still tested

    Build using doctest builder
    """

    builder = 'doctest'

    rst_sources=dict(a_page="""\
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


class TestNoRaises(PlotsBuilder):
    """ Confirm that exception, without raises option, generates error
    """
    should_error = True

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::

    # Another comment
    raise ValueError
""")


class TestRaisesOption(PlotsBuilder):
    """ Check raises option to nbplot directive proceeds without error
    """

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::
    :raises: ValueError

    # Another comment
    raise ValueError
""")

    def test_include_source_default(self):
        # Check that source still included
        assert_true('# Another comment' in self.get_built_file('a_page.html'))


class TestReference(PlotsBuilder):
    """ Check that reference is correctly generated.

    First check that the code gets built for html as predicted
    """

    builder = 'pseudoxml'

    rst_sources=dict(a_page="""\
A title
-------

.. _a-ref:

.. nbplot::

    >>> a = 1

See :ref:`the ref <a-ref>`.
""")

    def test_reference(self):
        # Check that reference correctly included
        built = self.get_built_file('a_page.pseudoxml')
        expected_regexp = re.compile(
r"""<document _plot_counter="1" source=".*?a_page.rst">
    <section ids="a-title" names="a\\ title">
        <title>
            A title
        <target ids="a-ref" names="a-ref">
        <nbplot_rendered>
            <doctest_block.*>
                >>> a = 1
            <.*>
        <paragraph>
            See\s
            <reference internal="True" refid="a-ref">
                <inline.*?>
                    the ref
            \.""", re.DOTALL)
        assert_true(expected_regexp.match(built))


class TestFlags(PlotsBuilder):
    """ Check flags get set correctly
    """

    builder = 'pseudoxml'

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot-flags::

    a = 1
    b = 2

.. nbplot-show-flags::

Some text

.. nbplot-flags::

    c = 3

.. nbplot-show-flags::
""")

    def test_flags(self):
        # Check that flags correctly set from flag directives
        built = self.get_built_file('a_page.pseudoxml')
        assert_true("""
        <title>
            A title
        <literal_block xml:space="preserve">
            {'a': 1, 'b': 2}
        <paragraph>
            Some text
        <literal_block xml:space="preserve">
            {'a': 1, 'b': 2, 'c': 3}""" in built)


class TestFlagsConfig(TestFlags):
    """ Check flags set from global config """

    conf_source=("""\
extensions = ["nb2plots.nbplots"]
nbplot_flags = {'flag1': 5, 'flag2': 6}
""")

    def test_flags(self):
        # Check that global flags merged with local
        built = self.get_built_file('a_page.pseudoxml')
        assert_true("""
        <title>
            A title
        <literal_block xml:space="preserve">
            {'a': 1, 'b': 2, 'flag1': 5, 'flag2': 6}
        <paragraph>
            Some text
        <literal_block xml:space="preserve">
            {'a': 1, 'b': 2, 'c': 3, 'flag1': 5, 'flag2': 6}"""
                    in built)


class TestSkips(PlotsBuilder):
    """ Check that doctest code can be skipped

    First check that the code gets built for html as predicted
    """
    builder = 'text'
    conf_source = ('extensions = ["nb2plots.nbplots", "sphinx.ext.doctest"]\n'
                   'nbplot_flags = {"skip": False}')

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::

    >>> # always
    >>> a = 'default'

Some text

.. nbplot::
    :render-parts: 1 if skip else 0

    >>> a = 'not skipped'

    .. part

    >>> a = 'yes too skipped'

Keep text coming

.. nbplot::
    :render-parts: 0 if skip else 1

    >>> a == 'yes too skipped again'
    True

    .. part

    >>> a == 'not skipped again'
    True
""")

    def test_html_pages(self):
        # Test txt pages always have main sections, regardless of selected
        # parts.
        html = self.get_built_file('a_page.txt')
        assert_true(">>> # always\n>>> a = 'default'" in html)
        assert_true(">>> a = 'not skipped'" in html)
        assert_true(">>> a = 'yes too skipped'" not in html)
        assert_true(">>> a == 'yes too skipped again'" in html)
        assert_true(">>> a == 'not skipped again'" not in html)


def test_part_finding():
    assert_equal(parse_parts([]), [{'contents': []}])
    assert_equal(parse_parts(['a = 1', 'b = 2']),
                             [{'contents': ['a = 1', 'b = 2']}])
    assert_equal(parse_parts(['a = 1', 'b = 2', '', '.. part', '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4']}])
    # Need blank lines between
    assert_equal(parse_parts(['a = 1', 'b = 2', '.. part', '', 'c = 4']),
                             [{'contents':
                               ['a = 1', 'b = 2', '.. part', '', 'c = 4']}]),
    assert_equal(parse_parts(['a = 1', 'b = 2', '', '.. part', 'c = 4']),
                             [{'contents':
                               ['a = 1', 'b = 2', '', '.. part', 'c = 4']}]),
    # Add some attributes
    assert_equal(parse_parts(['a = 1', 'b = 2', '',
                              '.. part', ' foo=bar', ' baz=boo',
                              '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4'],
                               'foo': 'bar', 'baz': 'boo'}])
    # Can have spaces around the equals
    assert_equal(parse_parts(['a = 1', 'b = 2', '',
                              '.. part', ' foo =bar', ' baz= boo',
                              '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4'],
                               'foo': 'bar', 'baz': 'boo'}])
    assert_equal(parse_parts(['a = 1', 'b = 2', '',
                              '.. part', ' foo = bar', ' baz=  boo',
                              '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4'],
                               'foo': 'bar', 'baz': 'boo'}])
    # Cannot continue on same line as part separator
    assert_equal(parse_parts(['a = 1', 'b = 2', '',
                              '.. part foo=bar',
                              '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2', '',
                              '.. part foo=bar',
                              '', 'c = 4']}])
    # Must be indentation
    assert_raises(ValueError,
                  parse_parts,
                  ['a = 1', 'b = 2', '',
                   '.. part', 'foo=bar',
                   '', 'c = 4'])
    # Must be same indentation
    assert_raises(ValueError,
                  parse_parts,
                  ['a = 1', 'b = 2', '',
                   '.. part', ' foo=bar', 'baz=boo',
                   '', 'c = 4'])
    assert_raises(ValueError,
                  parse_parts,
                  ['a = 1', 'b = 2', '',
                   '.. part', ' foo=bar', '  baz=boo',
                   '', 'c = 4'])
    # Add some attributes in the first part
    assert_equal(parse_parts(['.. part', ' mr=brightside', ' eager=eyes', '',
                              'a = 1', 'b = 2', '',
                              '.. part', ' foo=bar', ' baz=boo', '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2'],
                               'mr': 'brightside',
                               'eager': 'eyes'},
                              {'contents': ['c = 4'],
                               'foo': 'bar', 'baz': 'boo'}])
    # Contents with spaces, leading and trailing spaces skipped
    assert_equal(parse_parts(['a = 1', 'b = 2', '',
                              '.. part', ' foo=[1, 2, s]', ' bar= more stuff ',
                              '', 'c = 4']),
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4'],
                               'foo': '[1, 2, s]', 'bar': 'more stuff'}])
