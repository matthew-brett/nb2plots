# -*- coding: utf-8 -*-
""" Tests for nb2plots.nbplot extension
"""

from nb2plots import nbplots as nbp

from nose.tools import assert_equal

from nb2plots.tests import mockapp


def test_nbplots_setup():
    # Test extension setup works as expected
    app = mockapp.get_app()
    nbp.setup(app)
    config_names = ['nbplot_pre_code',
                    'nbplot_include_source',
                    'nbplot_html_show_source_link',
                    'nbplot_formats',
                    'nbplot_html_show_formats',
                    'nbplot_rcparams',
                    'nbplot_working_directory',
                    'nbplot_template',
                    'nbplot_flags']
    connects = [
        ('builder-inited', nbp.do_builder_init),
        ('env-purge-doc', nbp.do_purge_doc),
    ]
    for method_name, args, kwargs in app.method_calls:
        if (method_name == 'add_config_value' and
            args[0] in config_names):
            config_names.remove(args[0])
        if (method_name == 'connect' and args[0:2] in connects):
            connects.remove(args[0:2])
    assert_equal(len(config_names), 0,
                 'config set failed for {}'.format(config_names))
    assert_equal(len(connects), 0, 'Connections failed')
