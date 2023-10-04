##################
Releasing nb2plots
##################

* Review the open list of `nb2plots issues`_.  Check whether there are
  outstanding issues that can be closed, and whether there are any issues that
  should delay the release.  Label them.

* Review and update the release notes.  Review and update the :file:`Changelog`
  file.  Get a partial list of contributors with something like::

      git log 0.7.. | grep '^Author' | cut -d' ' -f 2- | sort | uniq

  where ``0.7`` was the last release tag name.

  Then manually go over ``git shortlog 0.7..`` to make sure the release notes
  are as complete as possible and that every contributor was recognized.

* Use the opportunity to update the ``.mailmap`` file if there are any
  duplicate authors listed from ``git shortlog -ns``.

* Check the copyright years in ``doc/conf.py`` and ``LICENSE``;

* Check the output of::

    rst2html.py README.rst > ~/tmp/readme.html

  because this will be the output used by PyPi_

* Check `nb2plots travis-ci`_.

* Once everything looks good, you are ready to upload the source release to
  PyPi.  See `setuptools intro`_.  Make sure you have a file
  ``\$HOME/.pypirc``, of form::


    [pypi]
    username = __token__

  This will in due course ask you for your PyPI token, for upload.

* Tag the release.  This will also set the version (we are using versioneer_
  to manage versions via git tags)::

    git tag -s 0.7

* Clean::

    # Check no files outside version control that you want to keep
    git status
    # Nuke
    git clean -fxd

* When ready::

    python -m build . --sdist
    twine upload dist/nb2plots*.tar.gz

* Upload the release commit and tag to github::

    git push
    git push --tags

.. include:: ../links_names.inc
