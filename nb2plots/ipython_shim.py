""" Shim for IPython before and after the big split
"""
try:
    import traitlets
    import traitlets.config as config
except ImportError:
    from IPython.utils import traitlets
    from IPython import config
try:
    import nbformat
except ImportError:
    from IPython import nbformat
try:
    import nbconvert
except ImportError:
    from IPython import nbconvert

# Use notebook format version 4 by default
nbf = nbformat.v4
