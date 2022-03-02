""" Tests for build using nbplot extension """
from __future__ import unicode_literals

from os.path import (join as pjoin, dirname, isdir)
import re
import os

from docutils.nodes import paragraph, title

import sphinx

SPHINX_ge_1p8 = sphinx.version_info[:2] >= (1, 8)

from nb2plots.nbplots import (run_code, parse_parts, nbplot_container,
                              nbplot_epilogue)
from sphinxtesters import SourcesBuilder

from nb2plots.testing import PlotsBuilder

from nb2plots.testing.nbtesters import assert_nb_equiv

import pytest


HERE = dirname(__file__)

# Variation in doctest block.
DOCTEST_BLOCK_RE = r'<doctest_block (classes="doctest" )?xml:space="preserve">'


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
    assert ns1['a'] == 10
    assert not 'b' in ns1
    # New namespace by default
    ns2 = run_code('b = 20')
    assert ns2['b'] == 20
    assert not 'a' in ns2
    # Adding to a namespace
    ns3 = run_code('c = 30', ns=ns1)
    assert ns3 is ns1
    assert ns1['c'] == 30
    # Checking raises
    run_code('d', raises=NameError)


class TestNbplots(SourcesBuilder):

    conf_source = ('extensions = ["nb2plots"]\n'
                   'nbplot_include_source = False\n')

    rst_sources = dict(a_page=get_otherpage('some_plots.rst'))

    def test_some_plots(self):
        assert isdir(self.out_dir)

        def plot_file(num):
            return pjoin(self.out_dir, 'a_page-{0}.png'.format(num))

        range_10, range_6, range_4 = [plot_file(i) for i in range(1, 4)]
        # Plot 5 is range(6) plot
        assert file_same(range_6, plot_file(5))
        # Plot 7 is range(4) plot
        assert file_same(range_4, plot_file(7))
        # Plot 8 uses the old range(4) figure and the new range(6) figure
        assert file_same(range_4, plot_file('8_00'))
        assert file_same(range_6, plot_file('8_01'))
        # Plot 9 shows the default close-figures behavior in action
        assert file_same(range_4, plot_file(9))
        # Plot 9 does not include source
        html_contents = self.get_built_file('a_page.html')
        # Plot 10 has included source
        assert '# Only a comment' in html_contents


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
        assert '# Only a comment' in html_contents
        # Plot 1 has no source link
        html_contents = self.get_built_file('a_page.html')
        assert 'href=".//a_page-1.py">Source code</a>' not in html_contents


class TestAnnoyingParens(PlotsBuilder):
    """ Test we've fixed the empty parens bug

    The matplotlib plotter puts an annoying empty open/close parens in the
    output when html source link is off, and there are no figures.
    """

    conf_source = ('extensions = ["nb2plots"]\n'
                   'nbplot_html_show_source_link = False')

    rst_sources = dict(a_page="""\
A title
-------

.. nbplot::

    # Only a comment
""")

    def test_annoying_parens(self):
        # Plot 1 has included source
        assert not '<p>()</p>' in self.get_built_file('a_page.html')


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
    conf_source = ('extensions = ["nb2plots"]\n'
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
        assert file_same(gpf('a_page', 1), red_bright)
        assert file_same(gpf('a_page', 3), blue_eager)
        assert file_same(gpf('b_page', 1), red_bright)


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
    conf_source=('extensions = ["nb2plots"]\n'
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
        assert 'a = 1' not in txt_contents
        assert 'b = 2' not in txt_contents
        assert 'a == 1' in txt_contents
        assert 'b == 2' in txt_contents
        assert 'c = 3' not in txt_contents


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
        assert '# Another comment' in self.get_built_file('a_page.html')


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
r"""<document _plot_counter="1" source=".*?a_page.rst"( xmlns.*)?>
    <section ids="a-title" names="a\\ title">
        <title>
            A title
        <target ids="a-ref" names="a-ref">
        <nbplot_container>
            <doctest_block.*>
                >>> a = 1
        <nbplot_epilogue>
            <.*>
        <paragraph>
            See\s
            <reference internal="True" refid="a-ref">
                <inline.*?>
                    the ref
            \.""", re.DOTALL)
        assert expected_regexp.match(built)


class TestFlags(PlotsBuilder):
    """ Check flags get set correctly
    """

    builder = 'pseudoxml'

    literal_header = (
        r'<literal_block ' +
        (r'force(_highlighting)?="False" language="default" linenos="False" '
        if SPHINX_ge_1p8 else '') +
        'xml:space="preserve">')

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
        expected = r"""
        <title>
            A title
        {literal_header}
            {{'a': 1, 'b': 2}}
        <paragraph>
            Some text
        {literal_header}
            {{'a': 1, 'b': 2, 'c': 3}}""".format(
                literal_header=self.literal_header)
        assert re.search(expected, built)


class TestFlagsConfig(TestFlags):
    """ Check flags set from global config """

    conf_source=("""\
extensions = ["nb2plots"]
nbplot_flags = {'flag1': 5, 'flag2': 6}
""")

    def test_flags(self):
        # Check that global flags merged with local
        built = self.get_built_file('a_page.pseudoxml')
        expected = r"""
        <title>
            A title
        {literal_header}
            {{'a': 1, 'b': 2, 'flag1': 5, 'flag2': 6}}
        <paragraph>
            Some text
        {literal_header}
            {{'a': 1, 'b': 2, 'c': 3, 'flag1': 5, 'flag2': 6}}""".format(
                literal_header=self.literal_header)
        assert re.search(expected, built)


class TestWithoutSkip(PlotsBuilder):
    """ Check that doctest code can be bracketed into skipped, not skipped

    First check that the code gets built for txt as predicted
    """
    builder = 'text'
    conf_source = ('extensions = ["nb2plots", "sphinx.ext.doctest"]\n'
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
    :run-parts: 1 if skip else 0

    >>> a = 'skip is False'

    .. part

    >>> a = 'skip is True'

Keep text coming

.. nbplot::
    :render-parts: 1 if skip else 2
    :run-parts: 1 if skip else 2

    >>> # An empty part, never used

    .. part

    >>> b = 'skip appears to be True'
    >>> a == 'skip is True'
    True

    .. part

    >>> b = 'skip appears to be False'
    >>> a == 'skip is False'
    True

Text continues

.. nbplot::
    :run-parts: 1 if skip else 0

    >>> # doctest only run when skip flag False, always rendered
    >>> b == 'skip appears to be False'
    True

    .. part

    >>> # only when skip flag True
    >>> b == 'skip appears to be True'
    True
""")

    def test_pages(self):
        # Test that the skip=False sections selected
        txt = self.get_built_file('a_page.txt')
        assert ">>> # always\n>>> a = 'default'" in txt
        assert ">>> a = 'skip is False'" in txt
        assert ">>> a = 'skip is True'" not in txt
        # Note ==, distinguishing from test above
        assert ">>> a == 'skip is True'" not in txt
        assert ">>> a == 'skip is False'" in txt
        assert ">>> b == 'skip appears to be False'" in txt
        assert ">>> b == 'skip appears to be True'" not in txt


class TestWithoutSkipDoctest(TestWithoutSkip):
    builder = 'doctest'

    def test_pages(self):
        # No pages built by doctest
        return


class TestWithoutSkipStructure(TestWithoutSkip):
    builder = 'pseudoxml'

    def test_pages(self):
        # Test that the skip=False sections selected
        p_xml = self.get_built_file('a_page.pseudoxml')
        regex = re.compile(
            r"""<document _plot_counter="\d" source=".+?">
    <section ids="a-title" names="a\\ title">
        <title>
            A title
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> # always
                >>> a = 'default'
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Some text
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> a = 'skip is False'
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Keep text coming
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> b = 'skip appears to be False'
                >>> a == 'skip is False'
                True
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Text continues
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> # doctest only run when skip flag False, always rendered
                >>> b == 'skip appears to be False'
                True""".format(**globals()))
        assert(regex.match(p_xml) is not None)


class TestWithSkip(TestWithoutSkip):
    """ Check that doctest code can be skipped according to flag
    """
    conf_source = ('extensions = ["nb2plots", "sphinx.ext.doctest"]\n'
                   'nbplot_flags = {"skip": True}')

    def test_pages(self):
        # Test that the skip=True sections selected
        txt = self.get_built_file('a_page.txt')
        assert ">>> # always\n>>> a = 'default'" in txt
        assert ">>> a = 'skip is False'" not in txt
        assert ">>> a = 'skip is True'" in txt
        # Note ==, distinguishing from test above
        assert ">>> a == 'skip is True'" in txt
        assert ">>> a == 'skip is False'" not in txt
        # The rendered version always has the first section, regardless of skip
        assert ">>> b == 'skip appears to be False'" in txt
        assert ">>> b == 'skip appears to be True'" not in txt


class TestWithSkipStructure(TestWithSkip):
    builder = 'pseudoxml'

    def test_pages(self):
        # Test that the skip=True sections selected
        p_xml = self.get_built_file('a_page.pseudoxml')
        regex = re.compile(
            r"""<document _plot_counter="\d" source=".+?">
    <section ids="a-title" names="a\\ title">
        <title>
            A title
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> # always
                >>> a = 'default'
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Some text
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> a = 'skip is True'
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Keep text coming
        <nbplot_container>
            {DOCTEST_BLOCK_RE}
                >>> b = 'skip appears to be True'
                >>> a == 'skip is True'
                True
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <paragraph>
            Text continues
        <nbplot_container hide-from="doctest">
            <dont_doctest_block xml:space="preserve">
                >>> # doctest only run when skip flag False, always rendered
                >>> b == 'skip appears to be False'
                True
        <nbplot_epilogue>
            <comment xml:space="preserve">
            <comment xml:space="preserve">
            <comment xml:space="preserve">
        <nbplot_container hide-from="all" show-to="doctest">
            {DOCTEST_BLOCK_RE}
                >>> # only when skip flag True
                >>> b == 'skip appears to be True'
                True""".format(**globals()))
        assert(regex.match(p_xml) is not None)


class TestWithSkipDoctest(TestWithSkip):
    builder = 'doctest'

    def test_pages(self):
        # No pages built by doctest
        return


class TestOtherWD(PlotsBuilder):
    """ Check that it is possible to run code with other working directory
    """

    rst_sources=dict(a_page="""\
A title
-------

.. nbplot::

    >>> # Code run during page generation, e.g. html build
    >>> import os
    >>> assert os.getcwd().endswith('my_wd')
    >>> # Working directory is on Python PATH
    >>> import funky_module
""")

    @classmethod
    def modify_source(cls):
        super(TestOtherWD, cls).modify_source()
        work_dir = pjoin(cls.build_path, 'my_wd')
        os.mkdir(work_dir)
        with open(pjoin(work_dir, 'funky_module.py'), 'wt') as fobj:
            fobj.write('# A funky module\n')
        with open(pjoin(cls.page_source, 'conf.py'), 'at') as fobj:
            fobj.write('\nnbplot_working_directory = "{}"\n'.format(work_dir))


class TestClearNotebook(PlotsBuilder):
    """ Test build of clear notebook with clearnotebook role
    """

    builder = 'text'

    rst_sources=dict(a_page="""\
A title
-------

:clearnotebook:`.`
:clearnotebook:`clear notebook <clear.ipynb>`
:fullnotebook:`full notebook <full.ipynb>`

Some text.

.. nbplot::

    >>> a = 1
    >>> a
    1
""")

    def test_pages(self):
        txt = self.get_built_file('a_page.txt')
        assert re.match(
            r'\n?A title\n\*{7}\n\n\nSome text.\n\n>>> a = 1\n>>> a\n1\n',
            txt)
        ipynb = self.get_built_file('a_page.ipynb')
        assert_nb_equiv(ipynb, r"""
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## A title\n",
    "\n",
    "\n",
    "\n",
    "\n",
    "Some text."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "a = 1\n",
    "a"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 1
}""")
        assert self.get_built_file('clear.ipynb') == ipynb
        full = self.get_built_file('full.ipynb')
        assert_nb_equiv(full, r"""
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## A title\n",
    "\n",
    "\n",
    "\n",
    "\n",
    "Some text."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "1"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "a = 1\n",
    "a"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 1
}""")


def test_part_finding():
    assert parse_parts([]) == [{'contents': []}]
    assert (parse_parts(['a = 1', 'b = 2']) ==
                             [{'contents': ['a = 1', 'b = 2']}])
    assert (parse_parts(['a = 1', 'b = 2', '', '.. part', '', 'c = 4']) ==
                             [{'contents': ['a = 1', 'b = 2']},
                              {'contents': ['c = 4']}])
    # Need blank lines between
    assert (parse_parts(['a = 1', 'b = 2', '.. part', '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2', '.. part', '', 'c = 4']}])
    assert (parse_parts(['a = 1', 'b = 2', '', '.. part', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2', '', '.. part', 'c = 4']}])
    # Add some attributes
    assert (parse_parts(['a = 1', 'b = 2', '',
                         '.. part', ' foo=bar', ' baz=boo',
                         '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2']},
             {'contents': ['c = 4'],
              'foo': 'bar', 'baz': 'boo'}])
    # Can have spaces around the equals
    assert (parse_parts(['a = 1', 'b = 2', '',
                         '.. part', ' foo =bar', ' baz= boo',
                         '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2']},
             {'contents': ['c = 4'],
              'foo': 'bar', 'baz': 'boo'}])
    assert (parse_parts(['a = 1', 'b = 2', '',
                         '.. part', ' foo = bar', ' baz=  boo',
                         '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2']},
             {'contents': ['c = 4'],
              'foo': 'bar', 'baz': 'boo'}])
    # Cannot continue on same line as part separator
    assert (parse_parts(['a = 1', 'b = 2', '',
                         '.. part foo=bar',
                         '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2', '',
                           '.. part foo=bar',
                           '', 'c = 4']}])
    # Must be indentation
    with pytest.raises(ValueError):
        parse_parts(['a = 1', 'b = 2', '',
                     '.. part', 'foo=bar',
                     '', 'c = 4'])
    # Must be same indentation
    with pytest.raises(ValueError):
        parse_parts(['a = 1', 'b = 2', '',
                     '.. part', ' foo=bar', 'baz=boo',
                     '', 'c = 4'])
    with pytest.raises(ValueError):
        parse_parts(['a = 1', 'b = 2', '',
                     '.. part', ' foo=bar', '  baz=boo',
                     '', 'c = 4'])
    # Add some attributes in the first part
    assert (parse_parts(['.. part', ' mr=brightside', ' eager=eyes', '',
                         'a = 1', 'b = 2', '',
                         '.. part', ' foo=bar', ' baz=boo', '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2'],
              'mr': 'brightside',
              'eager': 'eyes'},
             {'contents': ['c = 4'],
              'foo': 'bar', 'baz': 'boo'}])
    # Contents with spaces, leading and trailing spaces skipped
    assert (parse_parts(['a = 1', 'b = 2', '',
                         '.. part', ' foo=[1, 2, s]', ' bar= more stuff ',
                         '', 'c = 4']) ==
            [{'contents': ['a = 1', 'b = 2']},
             {'contents': ['c = 4'],
              'foo': '[1, 2, s]', 'bar': 'more stuff'}])


class TestHideShow(PlotsBuilder):
    """ Check that hide-from and show-to options respected
    """

    conf_source = ('extensions = ["nb2plots", "sphinx.ext.doctest"]\n')

    builder = 'text'

    rst_sources=dict(a_page="""\
#########
A section
#########

A plot that does not show its source (but does get run by doctest).

.. nbplot::
    :include-source: false

    >>> a = 1

The next incantation is nearly the same, except we also show the output in the
text builder (but no other).

.. nbplot::
    :hide-from: all
    :show-to: doctest text

    >>> b = 2

Here we hide the output from everything, including doctests, but show it to the
text builder again.

.. nbplot::
    :hide-from: all
    :show-to: text

    # Enigmatic sentence.

Show to everything (including doctest builder).

.. nbplot::

    >>> assert a == 1
    >>> assert b == 2

Hide from doctest builder, but no other.

.. nbplot::
    :hide-from: doctest

    >>> a = 99

Show that the doctest builder did not see the previous plot directive.

.. nbplot::

    >>> a == 1
    True
""")

    def test_hide_show(self):
        built = self.get_built_file('a_page.txt')
        expected = """\
A section
*********

A plot that does not show its source (but does get run by doctest).

The next incantation is nearly the same, except we also show the
output in the text builder (but no other).

>>> b = 2

Here we hide the output from everything, including doctests, but show
it to the text builder again.

   # Enigmatic sentence.

Show to everything (including doctest builder).

>>> assert a == 1
>>> assert b == 2

Hide from doctest builder, but no other.

>>> a = 99

Show that the doctest builder did not see the previous plot directive.

>>> a == 1
True
"""
        # Blank lines at beginning differ in Sphinx versions
        assert built.strip() == expected.strip()


class TestHideShowTests(TestHideShow):
    """ Test that the doctests pass, requining the hide/show to work
    """

    builder = 'doctest'

    def test_hide_show(self):
        # The build tests the doctests - here we test the doctree
        built = self.get_doctree('a_page')
        expected_node_types = [title] + [
            paragraph,
            nbplot_container,
            nbplot_epilogue] * 4
        for node, exp_type in zip(built[0].children, expected_node_types):
            assert type(node) == exp_type


class TestHideShowHtml(TestHideShow):
    """ Test that the HTML does not see the hidden section
    """

    builder = 'html'

    def test_hide_show(self):
        built = self.get_built_file('a_page.html')
        assert not '# Enigmatic sentence' in built
