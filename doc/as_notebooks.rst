################################
Using the as-notebooks directive
################################

The ``as-notebooks`` directive is a short cut for adding links to your ReST
page pointing to Jupyter notebooks.  When Sphinx sees this directive, it
converts the ReST page to notebooks, and add links to these notebooks in the
built HTML.  Use like this::

    .. as-notebooks::

Here is an example, generating very boring notebooks:

.. as-notebooks::

.. _as-notebooks-directive:

**********************
as-notebooks directive
**********************

.. automodule:: nb2plots.as_notebooks

.. include:: links_names.inc
