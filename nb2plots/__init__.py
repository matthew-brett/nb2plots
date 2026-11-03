# nb2plots package

# Update this version when making a release.
__version__ = "0.8.1a1"

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
