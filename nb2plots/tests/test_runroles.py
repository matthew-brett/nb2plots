""" Tests for to_notebook module
"""
from os.path import join as pjoin
from glob import glob
import re

from nb2plots import runroles as rr
from nb2plots import doctree2nb
from nb2plots import doctree2py
from nb2plots.converters import to_notebook
from nb2plots.ipython_shim import nbf
from nb2plots.converters import to_pxml

from nose.tools import assert_equal, assert_true

from nb2plots.tests import mockapp

from .convutils import fcontents, DATA_PATH


def test_runroles_setup(*args):
    # Test extension setup works as expected
    app = mockapp.get_app()
    rr.setup(app)
    connects = [('doctree-resolved', rr.collect_notebooks),
                ('build-finished', rr.write_notebooks)]
    roles = [('clearnotebook', rr.clearnotebook),
             ('fullnotebook', rr.fullnotebook)]
    translators = [('ipynb', doctree2nb.Translator),
                   ('python', doctree2py.Translator)]
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
    assert_nb_equiv(to_notebook.from_rst(rst_str), expected)


def test_example_files():
    # test sphinx2nb script over all .rst files checking against .ipynb files
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


def assert_rst_pxml(pxml_regex, rst_source):
    pxml = to_pxml.from_rst(rst_source)
    assert_true(re.match(pxml_regex, pxml))


def test_nb_role_doctrees():
    # Test that notebook roles generate expected doctrees
    expected_re_fmt = """\
<document source=".*?">
    <paragraph>
        Text then 
        <runrole_reference evaluate="{evaluate}" refdoc="contents" reftarget="{nb_base}.ipynb" reftype="{nb_type}notebook">
            {nb_text}
         then text."""

    def assert_rst_pxml(pxml_params, rst_source):
        pxml = to_pxml.from_rst(rst_source)
        pxml_regex = expected_re_fmt.format(**pxml_params)
        assert_true(re.match(pxml_regex, pxml))

    assert_rst_pxml(
        dict(evaluate='False',
             nb_base='contents',
             nb_type='clear',
             nb_text='Download this page as a Jupyter notebook'),
        "Text then :clearnotebook:`.` then text.")
    assert_rst_pxml(
        dict(evaluate='True',
             nb_base='contents',
             nb_type='full',
             nb_text='Download this page as a Jupyter notebook'),
        "Text then :fullnotebook:`.` then text.")
    assert_rst_pxml(
        dict(evaluate='False',
             nb_base='contents',
             nb_type='clear',
             nb_text='message to taste'),
        "Text then :clearnotebook:`message to taste` then text.")
    assert_rst_pxml(
        dict(evaluate='True',
             nb_base='contents',
             nb_type='full',
             nb_text='message to taste'),
        "Text then :fullnotebook:`message to taste` then text.")
    assert_rst_pxml(
        dict(evaluate='False',
             nb_base='foo',
             nb_type='clear',
             nb_text='message to taste'),
        "Text then :clearnotebook:`message to taste <foo.ipynb>` then text.")
    assert_rst_pxml(
        dict(evaluate='True',
             nb_base='foo',
             nb_type='full',
             nb_text='message to taste'),
        "Text then :fullnotebook:`message to taste <foo.ipynb>` then text.")
    assert_rst_pxml(
        dict(evaluate='False',
             nb_base='contents',
             nb_type='clear',
             nb_text='<foo.ipynb>'),
        "Text then :clearnotebook:`<foo.ipynb>` then text.")
    assert_rst_pxml(
        dict(evaluate='True',
             nb_base='contents',
             nb_type='full',
             nb_text='<foo.ipynb>'),
        "Text then :fullnotebook:`<foo.ipynb>` then text.")
