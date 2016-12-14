""" Tests for to_notebook module
"""
from os.path import join as pjoin, exists
from glob import glob

from nb2plots import to_notebook as tn
from nb2plots.to_notebook import sphinx2ipynb
from nb2plots.ipython_shim import nbf

from nose.tools import assert_equal

from nb2plots.tests import mockapp

from .convutils import convert_assert, fcontents, DATA_PATH


def test_to_notebook_setup(*args):
    # Test extension setup works as expected
    app = mockapp.get_app()
    tn.setup(app)
    connects = [('doctree-resolved', tn.collect_notebooks),
                ('build-finished', tn.write_notebooks)]
    roles = [('clearnotebook', tn.clearnotebook),
             ('fullnotebook', tn.fullnotebook)]
    translators = [('ipynb', tn.Translator)]
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'connect' and args[0:2] in connects):
            connects.remove(args[0:2])
        if (method_name == 'add_role' and args[0:2] in roles):
            roles.remove(args[0:2])
        if (method_name == 'set_translator' and args[0:2] in translators):
            translators.remove(args[0:2])

    assert_equal(len(connects), 0, 'Connections failed')
    assert_equal(len(roles), 0, 'Roles failed')
    assert_equal(len(translators), 0, 'Translators failed')


def assert_nb_equiv(ipynb, expected):
    actual_nb = nbf.reads(ipynb)
    expected_nb = nbf.reads(expected)
    # Ignore different minor versions of Notebook format
    # It does not appear to be possible to request specific minor versions of
    # the Notebook format.
    expected_nb['nbformat_minor'] = actual_nb['nbformat_minor']
    assert_equal(actual_nb, expected_nb)


def assert_conv_equal(rst_str, expected):
    assert_nb_equiv(sphinx2ipynb(rst_str), expected)


def test_example_files():
    # test sphinx2nb script over all .rst files checking against .ipynb files
    for rst_fname in glob(pjoin(DATA_PATH, '*.rst')):
        rst_contents = fcontents(rst_fname, 't')
        nb_fname = rst_fname[:-3] + 'ipynb'
        nb_contents = fcontents(nb_fname, 't')
        assert_conv_equal(rst_contents, nb_contents)


def test_notebook_basic():
    # Test conversion of basic ReST to ipynb JSON
    ipynb = sphinx2ipynb(r"""
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
    ipynb = sphinx2ipynb(r'Some text with $a = 1$ math.')
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
