##################################################
nb2plots - converting between notebooks and sphinx
##################################################

See the nb2plots documentation_ for more information.

.. shared-text-body

************
What it does
************

``nb2plots`` converts Jupyter_ notebooks to ReST_ files for Sphinx_, and back
again.

Nb2plots assumes that the ReST document will become the source for your Sphinx
web pages, but also for future versions of the notebook.  The notebook may
serve as a draft for the polished ReST page, and an output format from the
Sphinx build.  Why? Read on.

****************************************
Why convert Jupyter notebooks to Sphinx?
****************************************

Jupyter notebooks are just what the doctor ordered when hacking up a quick
tutorial, or preparing a software demo.  The problems start when you want to
do not-trivial edits to the notebooks, or you need features that notebooks
don't have, such as flexible cross-referencing, extensible markup, and so on.
Notebooks are also painful to use with version control.  These times make you
wish your notebook was in a standard extensible text format, such as ReST_.

You could convert your notebook to ReST using the standard `nbconvert`_
command, but this gives rather ugly ReST, and you lose all the nice code
execution and figure generation that the notebook is good at.

Enter Nb2plots.  The ``nb2plots`` command converts notebooks to specially
formatted ReST pages. Use with::

    nb2plots notebook.ipynb > with_plots.rst

Nb2plots converts your notebook to not-very-ugly ReST, where the code cells
become ``nbplot`` directives in your ReST file.

Specifically, a notebook code cell like this::

    a = 1

becomes (in the ReST document)::

    .. nbplot::

        >>> a = 1

The ``nbplot`` directives run the contained code when Sphinx builds your ReST
files, and embed the results of any plots that your code makes.  Actually,
``nbplot`` is an extended and edited version of the `matplotlib plot
directive`_.  Building your pages runs all the code and regenerates the
figures, and you get much of the reproducible goodness of the notebook
experience.

You can also run the standard Sphinx ``doctest`` extension over your pages to
check the doctest output of the code cells.

The ReST version of your notebook has many advantages - it is easier to edit
in your favorite text editor, and you can extend and configure the execution
and display of the code in several different ways.  For example, you can hide
some code cells (Nbplot directives) if the code is not interesting to your
point, but you still want the generated figure.  You can configure your Nbplot
directives to run different code for different configurations.  For these
options, see |nbplot-documentation|.  But - what do you lose, when going from
a notebook to a Nb2plots ReST document?

**********************************
I want notebooks and .py files too
**********************************

You may also want a version of your document that your users can execute.
Perhaps the page build is generating some tricky errors or warnings, and you
want to experiment with the code in the page interactively.  Perhaps your
users are used to notebooks, and prefer the code in that format.

Nb2plots also contains Sphinx extensions that cause the Sphinx build to
generate Python code files and Jupyter notebooks from the ReST source.  When
you add the Nb2plots ReST directive ``code-links`` to your ReST page, it will
cause the Sphinx build to create a Python code file and notebook versions of
your page, and adds download links to these versions::

    .. code-links::

See |code-links-documentation| for details.

**************************
Show me what it looks like
**************************

For a very simple example, see |worked-example|.

For a moderate-sized teaching site that makes extensive use of Nb2plots, see
https://matthew-brett.github.com/teaching.

************
Installation
************

::

    pip install nb2plots

You will need Pandoc_ installed and available as the ``pandoc`` command.

To install Pandoc on OSX, we recommend homebrew_::

    brew install pandoc

*************
Configuration
*************

Add the following to your Sphinx ``conf.py`` file::

    extensions = ["nb2plots"]

See |nbplot-documentation| for the various ``conf.py`` configuration settings.

****
Code
****

See https://github.com/matthew-brett/nb2plots

Released under the BSD two-clause license - see the file ``LICENSE`` in the
source distribution.

`travis-ci <https://travis-ci.org/matthew-brett/nb2plots>`_ kindly tests the
code automatically under Python versions 2.7, and 3.3 through 3.5.

The latest released version is at https://pypi.python.org/pypi/nb2plots

*****
Tests
*****

* Install ``nb2plots``
* Install the nose_ testing framework and the ``mock`` module::

    pip install nose mock

* Run the tests with::

    nosetests nb2plots

*******
Support
*******

Please put up issues on the `nb2plots issue tracker`_.

.. standalone-references

.. |nbplot-documentation| replace:: `nbplots documentation`_
.. |worked-example| replace:: `worked example`_
.. |code-links-documentation| replace:: `code-links documentation`_
.. _nbplots documentation:
    https://matthew-brett.github.com/nb2plots/nbplots.html
.. _code-links documentation:
    https://matthew-brett.github.com/nb2plots/code_links.html
.. _worked example:
    https://matthew-brett.github.com/nb2plots/worked_example.html
.. _documentation: https://matthew-brett.github.com/nb2plots
.. _pandoc: http://pandoc.org
.. _jupyter: jupyter.org
.. _homebrew: brew.sh
.. _sphinx: http://sphinx-doc.org
.. _rest: http://docutils.sourceforge.net/rst.html
.. _nb2plots issue tracker: https://github.com/matthew-brett/nb2plots/issues
.. _matplotlib plot directive: http://matplotlib.org/sampledoc/extensions.html
.. _nbconvert: http://nbconvert.readthedocs.org/en/latest/
.. _nose: http://readthedocs.org/docs/nose/en/latest
.. _nose: http://readthedocs.org/docs/nose/en/latest
.. _mock: https://github.com/testing-cabal/mock
