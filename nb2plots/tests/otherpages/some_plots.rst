##########
Some plots
##########

Plot 1:

.. nbplot::

    plt.plot(range(10))
    a = 99

Plot 2:

.. nbplot::

    plt.plot(range(6))

Plot 3 has length 4:

.. nbplot::

    plt.plot(range(4))

Plot 4 shows that a new block sees context created from the previous blocks:

.. nbplot::

    assert a == 99

Plot 5 defines ``a`` in a context block:

.. nbplot::

    plt.plot(range(6))
    a = 10

Plot 6 shows that a block sees the new variable.  It also uses
``:nofigs:``:

.. nbplot::
    :nofigs:

    assert a == 10
    b = 4

Plot 7 uses a variable previously defined in previous ``nofigs`` context. It
also closes any previous figures to create a fresh figure:

.. nbplot::

    assert b == 4
    plt.plot(range(b))

Plot 8 opens a new figure with ``keepfigs``.  The directive will plot both the first
and the second figure:

.. nbplot::
    :keepfigs:

    plt.figure()
    plt.plot(range(6))

Plot 9 shows the default behavior in action.  By default we close all figures
previous to this plot directive, so we get always plot the figure we create in
the directive:

.. nbplot::

    # Very unusual comment
    plt.figure()
    plt.plot(range(4))

Plot 10 uses ``include-source``:

.. nbplot::
    :include-source: true

    # Only a comment
