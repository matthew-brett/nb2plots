""" Test conversion of doctree to Jupyter notebook
"""

from nb2plots.doctree2nb import parse_doctest
from nb2plots.converters import to_notebook
from nb2plots.ipython_shim import nbf

# Shortcuts
n_nb = nbf.new_notebook
n_md_c = nbf.new_markdown_cell
n_c_c = nbf.new_code_cell

from nose.tools import assert_equal


def cells2json(cells):
    nb = nbf.new_notebook()
    nb['cells'] += cells
    return nbf.writes(nb)


def assert_rst_cells_equal(rst_text, cells):
    assert_equal(to_notebook.from_rst(rst_text), cells2json(cells))


def test_basic():
    assert_rst_cells_equal('Some text', [n_md_c('Some text')])


def test_notebook_reference():
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

.. only:: {}

    <h1>Something</h1>

After""".format(builder_name),
            [n_md_c('Before\n\nAfter')])
    assert_rst_cells_equal(
"""
Before

.. only:: markdown

    More text

After""".format(builder_name),
            [n_md_c('Before\n\nMore text\nAfter')])


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


def test_doctest_parser():
    assert_equal(parse_doctest('>>> # comment'), '# comment')
    assert_equal(parse_doctest('>>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10\n   >>> b = 20'),
                 'a = 10\nb = 20')
    assert_equal(parse_doctest(
        '   >>> for i in (1, 2):\n   ...     print(i)'),
        'for i in (1, 2):\n    print(i)')
