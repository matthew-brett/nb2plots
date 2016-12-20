###################
Scripts in nb2plots
###################

Nbplots installs the following command-line scripts:

* ``nb2plots`` |--| converts Jupyter notebooks to a ReST page with
  :doc:`nbplot directives <nbplots>` for the code cells;
* ``sphinx2py`` |--| converts a ReST page that may have nbplot directives or
  doctest blocks into a Python ``.py`` code file, where everything other than
  the nbplot directives and doctest blocks become comments in Markdown text
  format;
* ``sphinx2nb`` |--| converts a ReST page that may have nbplot directives or
  doctest blocks into a Jupyter notebook, where the nbplot directives and
  doctest blocks become code cells;
* ``sphinx2md`` |--| converts a ReST page into a Markdown page, where the
  conversion assumes the Sphinx versions of directives and roles;
* ``sphinx2pxml`` |--| converts a ReST page into a Sphinx pseudo XML page,
  where the conversion assumes the Sphinx versions of directives and roles;
* ``rst2md`` |--| converts a ReST page into a Markdown page, where the
  conversion assumes the `docutils`_ versions of directives and roles;

All these scripts write their output to standard output (stdout).

.. include:: links_names.inc
