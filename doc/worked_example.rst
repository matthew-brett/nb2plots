##############
Worked example
##############

Let's say I have a notebook `example notebook <example_notebook.html>`_.  You
can download this notebook from :download:`example_notebook.ipynb`.

I want to make this notebook into a ReST page to include in my Sphinx
project.  First I convert the notebook with the ``nb2plots`` script::

    nb2plots example_notebook.ipynb > converted_notebook.rst

This results in the ReST page `converted_example.rst
<_sources/converted_example.rst.txt>`_, which builds as HTML to
:doc:`converted_example`.

If you look at the `source of the converted notebook
<_sources/converted_example.rst.txt>`_ you will see two custom Nb2plots
directives:

* :ref:`nbplot <nbplot-directive>` |--| housing the content from the code
  cells in the original notebook;
* :ref:`mpl-interactive <mpl-interactive-directive>` |--| noting that the user
  may want to use the ``%matplotlib`` magic for interactive plots.

Notice that each Nbplot directive on a single page uses the same namespace, by
default, so the Nbplot directives on your page can build up variables in the
same way that a notebook does.

The notebook code cells convert to doctest blocks, so you can now check the
correctness of the code on your page with the Sphinx doctest extension:

.. code-block:: bash

    make doctest

This example page converts well, but, in practice, you may well want to edit
the ReST document to clean up some differences between the notebook code cells
and doctest blocks in Nbplot directives.

Now let us say that you would like to make this page available to your users
as Jupyter notebooks and / or a Python code file.  To do this, add the
following directive to the end of your page (or wherever you like):

.. code-block:: rest

    .. code-links::

See the :ref:`code-links-directive` for more detail.

When you do this, you get a built HTML page :doc:`like this
<converted_plus_notebooks>`.  Note the three links to the Python code file and
notebooks at the end of the page.  The first link is to the Python code file.
The second is to a notebook that has not been executed, and has no outputs.
The third is to a version of the same notebook that has been executed, and has
the code output cells.  See the :ref:`code-links-directive` documentation for
options to select which of these links to add.

.. include:: links_names.inc
