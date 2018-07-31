""" Skip the origin Gohlke transforms for doctests.

That file needs some specific doctest setup.
"""

from os.path import join as pjoin

collect_ignore = [pjoin('proj1', "conf.py"), 'rst_md_files']
