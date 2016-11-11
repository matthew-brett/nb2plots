# -*- coding: utf-8 -*-
""" Tests for nb2plots.nbplot extension
"""

try:
    # Python >=3.3
    from unittest import mock
except ImportError:
    import mock

from sphinx.application import Sphinx
from sphinx.config import Config

from nb2plots import nbplots as nbp

from nose.tools import assert_equal


def test_nbplots_setup():
    # Test extension setup works as expected
    app = mock.Mock(Sphinx)
    app.confdir = None
    app.config = mock.Mock(Config)
    nbp.setup(app)
    config_names = ['nbplot_rcparams',
                    'nbplot_pre_code',
                    'nbplot_include_source',
                    'nbplot_html_show_source_link',
                    'nbplot_formats',
                    'nbplot_basedir',
                    'nbplot_html_show_formats',
                    'nbplot_working_directory',
                    'nbplot_template']
    remaining_config_names = list(config_names)
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'add_config_value' and
            args[0] in remaining_config_names):
            remaining_config_names.remove(args[0])
    assert_equal(len(remaining_config_names), 0,
                 'config set failed for {}'.format(remaining_config_names))

    connects = (('env-purge-doc', nbp.clear_reset_marker),
                ('doctree-read', nbp.mark_plot_labels))
    remaining_connects = list(connects)
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'connect' and args[0:2] in connects):
            remaining_connects.remove(args[0:2])
    assert_equal(len(remaining_connects), 0, 'Connections failed')
