# ## Using the code-links directive
#
# The `code-links` directive is a short cut for adding links to your ReST page
# pointing to Python code files and Jupyter notebooks.  When Sphinx sees this
# directive, it converts the ReST page to a Python code file and notebooks, and
# add links to these files in the built HTML.  Use like this:
#
# ```
# .. code-links::
# ```
#
# Here is an example, generating very boring code and notebooks:
#
# ### code-links directive
#
# Directive to insert links to current document as runnable code.
#
# As a bare directive, with no options, inserts links to the current document as
# a Python code file; a clear notebook (no outputs) and a full notebook (outputs
# inserted by executing the built notebook):
#
# ```
# .. code-links:
# ```
#
# You can select one or more of these links with a list as an argument to the
# directive, where “python”, “clear” and “full” refer to a Python code file,
# clear notebook file and a full notebook file, respectively. For example:
#
# ```
# .. code-links: python
#
# .. code-links: python full
#
# .. code-links: clear full
# ```
#
# `python clear full` is the default.
#
# #### Kernel timeout
#
# When you build the full notebook, Jupyter will execute the code in each cell.
# By default, Jupyter will time out for any cell that takes longer than 30
# seconds to execute.  You can change this default for the whole project with the
# `fill_notebook_timeout` setting in the `conf.py` file (see below).  If you
# just want to change the setting for a single page, you can add the `timeout`
# option to the `code-links` directive.  For example:
#
# ```
# .. code-links:
#     :timeout: 120
# ```
#
# Set the `timeout` value to -1 or `none` to disable timeout entirely for
# this directive / page.
#
# #### Configuration options
#
# The code-links directive has the following configuration options, that can be
# set in the `conf.py` file.
#
# > fill_notebook_timeout
#
# > :   Default value for Jupyter kernel timeout when executing notebooks
# >     during page build.  If not set, default is 30 seconds. Set to -1 or
# >     None to disable timeout.
#
# <!-- links, substitutions to include across pages. -->
# <!-- vim: ft=rst -->
# <!-- This project -->
# <!-- Code support -->
# <!-- Relevant projects -->
# <!-- Python and common libraries -->
# <!-- Licenses -->
# <!-- Substitutions -->
