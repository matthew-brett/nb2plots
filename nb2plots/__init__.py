# nb2plots package

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from . import nbplots
from . import runroles
from . import mpl_interactive
from . import codelinks
from . import sphinx2foos


def setup_package():
    # Prevent nose tests running setup function
    pass


def setup(app):
    nbplots.setup(app)
    runroles.setup(app)
    mpl_interactive.setup(app)
    codelinks.setup(app)
    sphinx2foos.setup(app)
