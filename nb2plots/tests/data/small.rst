
Some text
=========

Some more test with mathematics :math:`a = b` and more:

.. math::


   b = c
   c = \vec{v}

Yet more text

.. nbplot::

    >>> import numpy as np
    >>> import matplotlib.pyplot as plt

.. mpl-interactive::


.. nbplot::

    >>> a = 2
    >>> b = a
    >>> b * a
    >>> for i in range(3):
    ...     c = a * i
    >>> c
    4

.. nbplot::

    >>> plt.plot(range(10))
    [...]



.. nbplot::

    >>> plt.plot(range(10))
    [...]



.. nbplot::

    >>> plt.imshow(np.arange(12).reshape((3, 4)))
    <...>



.. nbplot::

    >>> # Code that prints stuff with end result
    >>> print('one')
    >>> print('two')
    >>> 3
    3

    one
    two


.. nbplot::

    >>> # Code that prints stuff without end result
    >>> print('hello, again')

    hello, again

.. nbplot::

    >>> def xyz_trans_vol(vol, x_y_z_trans):
    ...     """ Make a new copy of `vol` translated by `x_y_z_trans` voxels
    ...
    ...     x_y_z_trans is a sequence or array length 3, containing the (x, y, z) translations in voxels.
    ...
    ...     Values in `x_y_z_trans` can be positive or negative, and can be floats.
    ...     """
    ...     x_y_z_trans = np.array(x_y_z_trans)

