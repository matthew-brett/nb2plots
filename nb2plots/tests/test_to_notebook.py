""" Tests for to_notebook module
"""

from nb2plots import to_notebook as tn
from nb2plots.to_notebook import sphinx2ipynb

from nose.tools import assert_equal

from nb2plots.tests import mockapp


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
    assert_equal(ipynb, expected)
