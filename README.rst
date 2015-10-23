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
nbconvert machinery, with the additional feature that code cells get converted
to Matplotlib plot directives (see: `matplotlib plot directive`_).

Specifically, a notebook code cell like this::

    a = 1

becomes (in the ReST document)::

    .. plot::
        :context:
        :nofigs:

        >>> a = 1

This allows you to make the output ReST file testable using the Sphinx doctest
builder, and the plots can be generated at Sphinx page build time.

You might consider adding these lines to your Sphinx ``conf.py`` file::

    # Config of plot_directive
    plot_include_source = True
    plot_html_show_source_link = False

This makes the code for the plot directive show up in the built document by
default. It also suppressed the default link to download the source code as a
``.py`` file.  You might prefer that when including the source in the
document, as the standalone ``.py`` file isn't very interesting when you can
already see the code, and the code is relatively short.

Note the ``:nofigs:`` option to the plot directive above.  nb2plots tries to
guess whether your code cell will generate a plot by looking for a generated
plot in the output cell following the code.   If nb2plots does not see a
plot in the notebook, it adds ``:nofigs:`` option, as here.  Of course, this
can go wrong when - for example - you haven't executed the notebook cell, so
you may need to go back and do some hand edits.

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
