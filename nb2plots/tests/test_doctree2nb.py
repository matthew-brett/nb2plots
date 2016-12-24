""" Test conversion of doctree to Jupyter notebook
"""
from os.path import join as pjoin
from glob import glob

from nb2plots.converters import to_notebook
from nb2plots.ipython_shim import nbf

# Shortcuts
n_nb = nbf.new_notebook
n_md_c = nbf.new_markdown_cell
n_c_c = nbf.new_code_cell

from nose.tools import assert_equal

from .convutils import fcontents, DATA_PATH


def cells2json(cells):
    nb = nbf.new_notebook()
    nb['cells'] += cells
    return nbf.writes(nb)


def assert_rst_cells_equal(rst_text, cells):
    actual = to_notebook.from_rst(rst_text)
    expected = cells2json(cells)
    assert_equal(actual, expected)


def test_basic():
    assert_rst_cells_equal('Some text', [n_md_c('Some text')])


def test_runrole_reference():
    # Ignore notebook reference in source ReST
    assert_rst_cells_equal('Some text :clearnotebook:`.`',
                           [n_md_c('Some text')])
    assert_rst_cells_equal('Some text :fullnotebook:`.`',
                           [n_md_c('Some text')])


def test_only():
    for builder_name in ('html', 'latex', 'unbelievable'):
        assert_rst_cells_equal(
"""
Before

.. only:: {0}

    Specific to builder {0}

After""".format(builder_name),
            [n_md_c('Before\n\nAfter')])
    assert_rst_cells_equal(
"""
Before

.. only:: markdown

    More text

After""".format(builder_name),
            [n_md_c('Before\n\nMore text\n\nAfter')])


def test_doctests():
    assert_rst_cells_equal("""\
Text 1

>>> # A comment
>>> a = 1

Text 2
""", [n_md_c('Text 1'), n_c_c('# A comment\na = 1'), n_md_c('Text 2')])


def test_nbplots():
    # nbplot directive with doctest markers
    assert_rst_cells_equal("""\
Text 1

.. nbplot::

    >>> # A comment
    >>> a = 1

Text 2
""", [n_md_c('Text 1'), n_c_c('# A comment\na = 1'), n_md_c('Text 2')])
    # nbplot directive with no doctest markers
    assert_rst_cells_equal("""\
Text 1

.. nbplot::

    # A comment
    a = 1

Text 2
""", [n_md_c('Text 1'), n_c_c('# A comment\na = 1'), n_md_c('Text 2')])
    # Doctest interspersed with text
    assert_rst_cells_equal("""\
Text 1

.. nbplot::

    >>> # A comment

    Some thoughts I had

    >>> a = 1

Text 2
""", [n_md_c('Text 1'),
      n_c_c('# A comment'),
      n_md_c('Some thoughts I had'),
      n_c_c('a = 1'),
      n_md_c('Text 2')])


def assert_nb_equiv(ipynb, expected):
    actual_nb = nbf.reads(ipynb)
    expected_nb = nbf.reads(expected)
    # Ignore different minor versions of Notebook format
    # It does not appear to be possible to request specific minor versions of
    # the Notebook format.
    expected_nb['nbformat_minor'] = actual_nb['nbformat_minor']
    assert_equal(actual_nb, expected_nb)


def assert_conv_equal(rst_str, expected):
    assert_nb_equiv(to_notebook.from_rst(rst_str), expected)


def test_example_files():
    # test conversion over all .rst files, checking against .ipynb files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = fcontents(rst_fname, 't')
        nb_fname = rst_fname[:-3] + 'ipynb'
        nb_contents = fcontents(nb_fname, 't')
        assert_conv_equal(rst_contents, nb_contents)


def test_notebook_basic():
    # Test conversion of basic ReST to ipynb JSON
    ipynb = to_notebook.from_rst(r"""
Title
=====

Some text with :math:`a = 1` math.

.. math::

    \textrm{math block}

.. nbplot::

    >>> c = 1
    >>> c
    1

More text.

.. nbplot::

    >>> d = 2
    >>> d
    2""")
    expected = r"""{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Title\n",
    "\n",
    "Some text with $a = 1$ math.\n",
    "\n",
    "$$\n",
    "\\textrm{math block}\n",
    "$$"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "c = 1\n",
    "c"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "More text."
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "d = 2\n",
    "d"
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 1
}"""
    assert_nb_equiv(ipynb, expected)


def test_default_mathdollar():
    # Test mathdollar extension present by default.
    ipynb = to_notebook.from_rst(r'Some text with $a = 1$ math.')
    expected = r"""{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "Some text with $a = 1$ math."
   ]
  }
 ],
 "metadata": {},
 "nbformat": 4,
 "nbformat_minor": 1
}"""
    assert_nb_equiv(ipynb, expected)


