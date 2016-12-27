""" Test whether doc examples same as previously
"""

from os.path import join as pjoin, dirname

from nb2plots.from_notebook import convert_nb_fname
from nb2plots.converters import to_py, to_notebook

from .convutils import fcontents
from .test_doctree2nb import assert_nb_equiv

from nose.tools import assert_equal

HERE = dirname(__file__)
DATA = pjoin(HERE, 'data')


def test_regression():
    # Test documentation worked example
    input_nb_fname = pjoin(DATA, 'example_notebook.ipynb')
    output_rst_fname = pjoin(DATA, 'converted_example.rst')
    # Convert to ReST, add trailing CR from output script
    rst = convert_nb_fname(input_nb_fname) + '\n'
    assert_equal(rst.encode('utf8'), fcontents(output_rst_fname))
    # Convert ReST to output formats
    py_file = to_py.from_rst(rst)
    assert_equal(py_file.encode('utf8'),
                 fcontents(pjoin(DATA, 'converted_plus_notebooks.py')))
    ipy_file = to_notebook.from_rst(rst)
    assert_nb_equiv(ipy_file,
                 fcontents(pjoin(DATA, 'converted_plus_notebooks.ipynb'))
                    .decode('utf8'))
