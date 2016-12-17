#########################################
Improving the ReST to Markdown conversion
#########################################

Nb2plots includes a converter from ReST to Markdown.  As you will see in the
``LICENSE`` file, the basis for this converter comes from the `rst2md
project`_ by Chris Wrench, with thanks.  At the time of writing (December
2016) the Nb2plots converter could deal with a considerably larger range of
Markdown than the original rst2md project.  However, the converter still does
not deal specifically with a fairly large number of Sphinx / ReST constructs,
so we would be very grateful for your help in improving the converter.  These
are some hints how to go about that.

**************************************************
Workflow for improving ReST to Markdown conversion
**************************************************

* Set yourself up with a git fork and clone of the `nb2plots code`_.  Install
  the development code with something like:

  .. code-block:: bash

      pip install -e .

  from the root ``nb2plots`` directory (the directory containing the
  ``setup.py`` file.

* Make sure the current tests pass with:

  .. code-block:: bash

      nosetests nb2plots

* Identify a ReST construct you would like to handle, or handle better. Let's
  say you you've decided to make the converter do something sensible with the
  ``:PEP:`` text role in ReST;

* Make a new ReST file that uses the construct, and put it in the
  ``nb2plots/tests/rst_md_files`` directory.  For example your file could be
  ``nb2plots/tests/rst_md_files/pep.rst`` with contents:

  .. code-block:: rest

    Test converting the :pep:`8` text role to Markdown

  The file have any name, as long as it has a ``.rst`` extension.

* If your construct is valid in vanilla `docutils`_ ReST, then run the
  ``rst2md`` converter over the file and see what it looks like.  In the case
  of the ``pep`` text role, you might see a message that the ``pep`` role is
  not yet supported, and the output will omit the ``pep`` role contents:

  .. code-block:: bash

    rst2md nb2plots/tests/rst_md_files/pep.rst

* If your construct is only valid for Sphinx_ ReST, then run the ``sphinx2md``
  converter on it, so see what happens:

  .. code-block:: bash

    sphinx2md nb2plots/tests/rst_md_files/pep.rst

* Now have a look at the code in the ``nb2plots.doctree2md`` module.  Add new
  ``visit_`` / ``depart_`` methods or modify the existing methods to handle
  your construct better.  Try the ``rst2md`` and ``sphinx2md`` commands on the
  ReST file to see what the output looks like;

* When you are satisfied, write the current output of ``rst2md`` to the
  ``rst_md_files`` directory with a ``.md`` extension:

  .. code-block:: bash

    rst2md nb2plots/tests/rst_md_files/pep.rst > nb2plots/tests/rst_md_files/pep.md

  If the ``sphinx2md`` script should give a different output, write that
  output with a ``.smd`` extension:

  .. code-block:: bash

    sphinx2md nb2plots/tests/rst_md_files/pep.rst > nb2plots/tests/rst_md_files/pep.smd

* Run the relevant tests:

  .. code-block:: bash

      nosetests nb2plots/tests/test_doctree2md.py
      nosetests nb2plots/tests/test_sphinx2md.py

  These will test your new ReST file, and the various other example ReST
  files, against their expected Markdown outputs.

* Once the relevant tests are fixed, run all the tests to check that the rest
  of the code (such as notebook conversion) is still working as expected.  If
  the tests fail, but you think your output is better than the previous output
  that the tests are using, feel free to edit.

  .. code-block:: bash

      nosetests nb2plots

* Make a pull request to `nb2plots github`_.

.. include:: ../links_names.inc
