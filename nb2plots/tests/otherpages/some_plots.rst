##########
Some plots
##########

Plot 1 does not use context:

.. nbplot::

    plt.plot(range(10))
    a = 10

Plot 2 doesn't use context either; has length 6:

.. nbplot::

    plt.plot(range(6))

Plot 3 has length 4:

.. nbplot::

    plt.plot(range(4))

Plot 4 shows that a new block with context does not see the variable defined
in the no-context block:

.. nbplot::
    :context:

    assert 'a' not in globals()

Plot 5 defines ``a`` in a context block:

.. nbplot::
    :context:

    plt.plot(range(6))
    a = 10

Plot 6 shows that a block with context sees the new variable.  It also uses
``:nofigs:``:

.. nbplot::
    :context:
    :nofigs:

    assert a == 10
    b = 4

Plot 7 uses a variable previously defined in previous ``nofigs`` context. It
also closes any previous figures to create a fresh figure:

.. nbplot::
    :context: close-figs

    assert b == 4
    plt.plot(range(b))

Plot 8 shows that a non-context block still doesn't have ``a``:

.. nbplot::
    :nofigs:

    assert 'a' not in globals()

Plot 9 has a context block, and does have ``a``:

.. nbplot::
    :context:
    :nofigs:

    assert a == 10

Plot 10 resets context, and ``a`` has gone again:

.. nbplot::
    :context: reset
    :nofigs:

    assert 'a' not in globals()
    c = 10

Plot 11 continues the context, we have the new value, but not the old:

.. nbplot::
    :context:

    assert c == 10
    assert 'a' not in globals()
    plt.plot(range(c))

Plot 12 opens a new figure.  By default the directive will plot both the first
and the second figure:

.. nbplot::
    :context:

    plt.figure()
    plt.plot(range(6))

Plot 13 shows ``close-figs`` in action.  ``close-figs`` closes all figures
previous to this plot directive, so we get always plot the figure we create in
the directive:

.. nbplot::
    :context: close-figs

    # Very unusual comment
    plt.figure()
    plt.plot(range(4))

Plot 14 uses ``include-source``:

.. nbplot::
    :include-source: true

    # Only a comment
