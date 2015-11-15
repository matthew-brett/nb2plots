##################################################
nb2plots - converting between notebooks and sphinx
##################################################

************
What it does
************

nb2plots currently only converts IPython notebooks to ReST_ files for Sphinx_.

Use with::

    nb2plots notebook.ipynb > with_plots.rst

This converts the IPython notebook to Restructured text using the normal
nbconvert_ machinery, with the additional feature that code cells get
converted to a custom ``nbplot`` plot directives based on the `matplotlib plot
directive`_.

Specifically, a notebook code cell like this::

    a = 1

becomes (in the ReST document)::

    .. nbplot::

        >>> a = 1

This allows you to make the output ReST file testable using the Sphinx doctest
builder, and the plots can be generated at Sphinx page build time.

In order to make this ``nbplot`` directive work for your sphinx builds, you
should add the following to your ``conf.py`` file::

    extensions = ["nb2plots.nbplots"]

The ``nbplot`` directive is very similar to the ``plot`` directive of
matplotlib, and started life as a fork of that code.  It differs mainly in
that its default is to keep the namespace from one ``nbplot`` directive to the
next in a given page, and has output defaults adapted to directive contents
with source code rather than pointing to a standalone script.  See the
docstring of ``nb2plots/nbplots.py`` for details.

************
Dependencies
************

You will need pandoc_ installed and available as the ``pandoc`` command.

For OSX, we recommend homebrew_ for installing pandoc::

    brew install pandoc

****
Code
****

See https://github.com/matthew-brett/nb2plots

Released under the BSD two-clause license - see the file ``LICENSE`` in the
source distribution.

`travis-ci <https://travis-ci.org/matthew-brett/nb2plots>`_ kindly tests the
code automatically under Python versions 2.6 through 2.7, and 3.2 through 3.5.

The latest released version is at https://pypi.python.org/pypi/nb2plots

*******
Support
*******

Please put up issues on the `nb2plots issue tracker`_.

.. _pandoc: http://pandoc.org
.. _homebrew: brew.sh
.. _sphinx: http://sphinx-doc.org
.. _rest: http://docutils.sourceforge.net/rst.html
.. _nb2plots issue tracker: https://github.com/matthew-brett/nb2plots/issues
.. _matplotlib plot directive: http://matplotlib.org/sampledoc/extensions.html
.. _nbconvert: http://nbconvert.readthedocs.org/en/latest/
