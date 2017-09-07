###########
Nbplot file
###########

Introducing...

.. nbplot::

    >>> a = 1
    >>> a
    1

... the ``nbplot``.

.. nbplot::

    >>> b = 1
    >>> a
    1

.. mpl-interactive::

A block to test line-wrapping:

.. nbplot::

    >>> # Here is a comment line that goes beyond the normal 80 character line wrap to test (non) wrapping

Markdown builder can be forced to skip:

.. nbplot::
    :hide-from: markdown

    >>> # Should not appear in Markdown

Python builder can be forced to skip:

.. nbplot::
    :hide-from: python

    >>> # Should not appear in Python

Jupyter builder can be forced to skip:

.. nbplot::
    :hide-from: jupyter

    >>> # Should not appear in Notebook
