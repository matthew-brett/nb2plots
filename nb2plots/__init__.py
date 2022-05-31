# nb2plots package

from . import _version
__version__ = _version.get_versions()['version']

from . import nbplots
from . import runroles
from . import mpl_interactive
from . import codelinks
from . import sphinx2foos


def setup(app):
    nbplots.setup(app)
    runroles.setup(app)
    mpl_interactive.setup(app)
    codelinks.setup(app)
    sphinx2foos.setup(app)
