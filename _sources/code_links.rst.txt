.. _code-links-documentation:

##############################
Using the code-links directive
##############################

The ``code-links`` directive is a short cut for adding links to your ReST page
pointing to Python code files and Jupyter notebooks.  When Sphinx sees this
directive, it converts the ReST page to a Python code file and notebooks, and
add links to these files in the built HTML.  Use like this:

.. code-block:: rest

    .. code-links::

Here is an example, generating very boring code and notebooks:

.. code-links::

.. _code-links-directive:

********************
code-links directive
********************

.. automodule:: nb2plots.codelinks

.. include:: links_names.inc
