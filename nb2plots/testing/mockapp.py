""" Mocking Sphinx apps for testing
"""

try:
    # Python >=3.3
    from unittest import mock
except ImportError:
    import mock

from sphinx.application import Sphinx
from sphinx.config import Config


def get_app():
    app = mock.Mock(Sphinx)
    app.confdir = None
    app.config = mock.Mock(Config)
    return app
