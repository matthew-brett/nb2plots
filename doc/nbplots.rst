##########################
Using the nbplot directive
##########################

The ``nbplot`` directive is very similar to the `matplotlib plot directive`_,
and started life as a fork of that code.  It differs mainly in that its
default is to keep the name-space from one ``nbplot`` directive to the next in
a given page.  It also has output defaults adapted to directive contents with
source code rather than pointing to a standalone script.

For example, here is the source for an Nbplot directive::

    .. nbplot::

        >>> a = 1
        >>> a
        1

This renders as:

.. nbplot::

    >>> a = 1
    >>> a
    1

All Nbplot directives in a page share a namespace with the first (by default).
Here is another Nbplot directive:

.. nbplot::

    >>> b = a
    >>> b
    1

Nbplot directives can also make |--| plots:

.. nbplot::

    >>> import matplotlib.pyplot as plt
    >>> plt.plot(range(10))

Notice that the HTML version of the page contains links to high and low
resolution PNG versions of the plot, and a PDF version.

The code in Nbplot directives gets executed during the page build, so your
build will detect any errors.   With doctest code blocks, like the above, you
can also test the doctest output, using the Sphinx ``doctest`` builder, which
you might be able to run with::

    make doctest

See the ``run-parts`` and ``render-parts`` options to run and render different
code according to your local configuration.

.. _nbplot-directive:

****************
nbplot directive
****************

.. automodule:: nb2plots.nbplots

.. include:: links_names.inc
