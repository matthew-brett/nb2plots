########################################
Test Sphinx builds on an example project
########################################

If you've developed Sphinx extensions before, you'll know that they can be
hard to test.

Have a look at the machinery in ``nb2plots/sphinxutils.py`` for a somewhat
general way of writing tests for Sphinx builds, and
``nb2plots/tests/test_nbplots.py`` for many examples using that machinery.

Sometimes, what you really want to do, is try an actual Sphinx build from the
command line.

At least, that is what I often want to do, so I made an example Sphinx project
to play with at ``nb2plots/tests/futz``.  To get started:

.. code-block:: bash

    cd nb2plots/tests/futz
    make init

Now you can edit the files in the example Sphinx project in the ``proj1``
directory.  For example, you might want to try out some ReST by editing the
example page ``proj1/a_page.rst``.  Try the HTML build with:

.. code-block:: bash

    make html

Have a look at the simple ``Makefile`` for some other ``make`` targets.
