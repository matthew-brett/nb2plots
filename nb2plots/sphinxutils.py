""" Utilties for running sphinx tasks in-process
"""

from os.path import join as pjoin
import shutil
from contextlib import contextmanager
from copy import copy
from tempfile import mkdtemp

from docutils import nodes
from docutils.parsers.rst import directives, roles
from sphinx.application import Sphinx

fresh_roles = copy(roles._roles)
fresh_directives = copy(directives._directives)
fresh_visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()


def reset_class(cls, original_dict):
    for key in list(cls.__dict__):
        if key not in original_dict:
            delattr(cls, key)
        else:
            setattr(cls, key, original_dict[key])


class TestApp(Sphinx):

    def __init__(self, *args, **kwargs):
        self._set_cache()
        with self.own_namespace():
            super(TestApp, self).__init__(*args, **kwargs)

    def _set_cache(self):
        self._docutils_cache = dict(
            directives=copy(fresh_directives),
            roles=copy(fresh_roles),
            visitor_dict = fresh_visitor_dict)

    @contextmanager
    def own_namespace(self):
        """ Set docutils namespace for builds """
        cache = self._docutils_cache
        _directives = directives._directives
        _roles = roles._roles
        _visitor_dict = nodes.GenericNodeVisitor.__dict__.copy()
        directives._directives = cache['directives']
        roles._roles = cache['roles']
        reset_class(nodes.GenericNodeVisitor, cache['visitor_dict'])
        try:
            yield
        finally:
            directives._directives = _directives
            roles._roles = _roles
            reset_class(nodes.GenericNodeVisitor, _visitor_dict)

    def build(self, *args, **kwargs):
        with self.own_namespace():
            return super(TestApp, self).build(*args, **kwargs)


DEFAULT_CONF =  """\
extensions = ["nb2plots.nbplots",
              "nb2plots.to_notebook"]
"""


class TempApp(TestApp):
    """ An application running in its own temporary directory
    """

    def __init__(self, rst_text, conf_text=None, buildername='html',
                 warningiserror=True, conf_dir=None):
        if conf_dir is None and conf_text is not None:
            raise ValueError('conf_text must be None if conf_dir set')
        conf_text = DEFAULT_CONF if conf_text is None else conf_text
        tmp_dir = mkdtemp()
        self.tmp_dir = tmp_dir
        if conf_dir is None:
            conf_dir = tmp_dir
            with open(pjoin(tmp_dir, 'conf.py'), 'wt') as fobj:
                fobj.write(conf_text)
        with open(pjoin(tmp_dir, 'contents.rst'), 'wt') as fobj:
            fobj.write(rst_text)
        # Write a default index file in case we're using a conf file that needs
        # it.
        with open(pjoin(tmp_dir, 'index.rst'), 'wt') as fobj:
            fobj.write("""\
.. toctree::
    :hidden:

    contents
    index
""")
        self._set_cache()
        with self.own_namespace():
            TestApp.__init__(self,
                             tmp_dir,
                             conf_dir,
                             tmp_dir,
                             tmp_dir,
                             buildername,
                             warningiserror=warningiserror)

    def __del__(self):
        shutil.rmtree(self.tmp_dir)


def build_rst(rst_text, conf_text=None, conf_dir=None):
    app = TempApp(rst_text, conf_text, conf_dir=conf_dir)
    app.build(False, [])
    doctree = app.env.get_doctree('contents')
    return app, doctree
