""" Test conversion of doctree to Jupyter notebook
"""

from docutils.io import StringOutput

from nb2plots import doctree2nb as d2nb
from nb2plots.doctree2nb import parse_doctest
from nb2plots.to_notebook import nbf
# Shortcuts
n_nb = nbf.new_notebook
n_md_c = nbf.new_markdown_cell
n_c_c = nbf.new_code_cell

from .pagebuilder import TestApp
from nb2plots.tmpdirs import dtemporize

from nose.tools import assert_equal


DEFAULT_CONF =  """\
extensions = ["nb2plots.nbplots",
              "nb2plots.to_notebook"]
"""


@dtemporize
def build_rst(rst_text, conf_text=DEFAULT_CONF):
    with open('conf.py', 'wt') as fobj:
        fobj.write(conf_text)
    with open('contents.rst', 'wt') as fobj:
        fobj.write(rst_text)
    app = TestApp('.', '.', '.', '.', 'html', warningiserror=True)
    with app.own_namespace():
        app.build(False, [])
        doctree = app.env.get_doctree('contents')
    return app, doctree


def rst2ipynb(rst_text):
    writer = d2nb.Writer()
    app, doctree = build_rst(rst_text)
    destination = StringOutput(encoding='utf8')
    return writer.write(doctree, destination)


def cells2json(cells):
    nb = nbf.new_notebook()
    nb['cells'] += cells
    return nbf.writes(nb).encode('utf8')


def test_basic():
    assert_equal(rst2ipynb('Some text'),
                 cells2json([n_md_c('Some text')]))
    assert_equal(rst2ipynb("""\
Text 1

>>> # A comment
>>> a = 1

Text 2
"""), cells2json([n_md_c('Text 1'),
                  n_c_c('# A comment\na = 1'),
                  n_md_c('Text 2')]))


def test_doctest_parser():
    assert_equal(parse_doctest('>>> # comment'), '# comment')
    assert_equal(parse_doctest('>>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10'), 'a = 10')
    assert_equal(parse_doctest('   >>> a = 10\n   >>> b = 20'),
                 'a = 10\nb = 20')
    assert_equal(parse_doctest(
        '   >>> for i in (1, 2):\n   ...     print(i)'),
        'for i in (1, 2):\n    print(i)')
