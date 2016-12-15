# nb2plots package

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from . import nbplots
from . import to_notebook
from . import mpl_interactive


def setup_package():
    # Prevent nose tests running setup function
    pass


def setup(app):
    nbplots.setup(app)
    to_notebook.setup(app)
    mpl_interactive.setup(app)
