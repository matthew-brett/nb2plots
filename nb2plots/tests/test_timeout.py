""" Test that timeout parameters work as expected
"""

from os.path import join as pjoin, isfile

from nb2plots.testing import PlotsBuilder


class _CheckTimeout(PlotsBuilder):
    """ Machinery for checking timeout
    """

    rst_sources = {'a_page': r"""\
Title
#####

.. code-links::

.. nbplot::

    >>> from time import sleep
    >>> sleep(5)
"""}


class TestNoTimeout(_CheckTimeout):
    """ The default timeout is fairly long, so a short wait is OK

    ``ExecutePreprocessor`` in ``nbconvert/preprocessors/execute.py`` suggests
    default is 30 seconds.
    """

    def test_output(self):
        assert isfile(pjoin(self.out_dir, 'a_page_full.ipynb'))


class TestCLOptsTimeout(_CheckTimeout):
    """ Set timeout to 1 second with code-link option, build should error
    """

    rst_sources = {'a_page': r"""\
Title
#####

.. code-links::
    :timeout: 1

.. nbplot::

    >>> from time import sleep
    >>> sleep(5)
"""}

    should_error = True


class TestFTimeout(_CheckTimeout):
    """ Set timeout to 1 second with role option, build should error
    """

    rst_sources = {'a_page': r"""\
Title
#####

.. role:: longerfullnotebook(fullnotebook)
   :timeout: 1

Add :longerfullnotebook:`.`

.. nbplot::

    >>> from time import sleep
    >>> sleep(5)
"""}

    should_error = True


class TestConfTimeout(_CheckTimeout):
    """ Set timeout to 1 second with conf.py option, build should error
    """

    conf_source = (TestNoTimeout.conf_source +
                   '\nfill_notebook_timeout = 1')

    should_error = True


class TestConfigCLTimeout(TestNoTimeout):
    """ Code-links options overrides configuration option
    """

    conf_source = (TestNoTimeout.conf_source +
                   '\nfill_notebook_timeout = 1')

    rst_sources = {'a_page': r"""\
Title
#####

.. code-links::
    :timeout: 10

.. nbplot::

    >>> from time import sleep
    >>> sleep(5)
"""}


class TestBestTimeout(TestNoTimeout):
    """ Check that multiple links to same notebook use longest timeout
    """

    rst_sources = {'a_page': r"""\
Title
#####

.. code-links::
    :timeout: 1

.. role:: shorterfullnotebook(fullnotebook)
   :timeout: 2

Add :shorterfullnotebook:`short <short.ipynb>`

.. role:: longerfullnotebook(fullnotebook)
   :timeout: 10

Add :longerfullnotebook:`long <long.ipynb>`

.. nbplot::

    >>> from time import sleep
    >>> sleep(5)
"""}
