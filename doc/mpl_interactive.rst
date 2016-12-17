###################################
Using the mpl-interactive directive
###################################

Many notebooks have code cells generating matplotlib_ plots.  Nearly all of
these have a code cell near the top with the IPython magic command
``%matplotlib inline`` or ``%matplotlib nbagg``.  This commands tell the
notebook to embed the plots inside the notebook rather than generate them in
separate windows.

When ``nb2plots`` converts a notebook to ReST, it detects these commands, and
adds a new directive ``.. mpl-interactive::`` at the matching place in the
ReST page.  When Sphinx builds the ReST page to HTML, the directive put
boilerplate text into the page reminding the user that they may want to use
the ``%matplotlib`` magic command in the IPython_ console, or ``%matplotlib
inline`` when they are running the commands in the Jupyter notebook.  The
``mpl-interactive`` directive also serves as marker when converting the ReST
page to a notebook again; the directive generates a notebook code cell with
the ``%matplotlib inline`` magic at the matching location, like this:

.. mpl-interactive::

.. _mpl-interactive-directive:

*************************
mpl-interactive directive
*************************

.. automodule:: nb2plots.mpl_interactive

.. include:: links_names.inc
