##################
Releasing nb2plots
##################

Check `nb2plots travis-ci`_.

::

    git tag -s 0.1
    git clean -fxd
    python setup.py register
    python setup.py sdist --formats=gztar,zip upload --sign
    git push
    git push --tags

.. _nb2plots travis-ci: https://travis-ci.org/matthew-brett/nb2plots
