""" Directive to handle %matplotlib [inline] in Sphinx, notebooks
"""

from docutils.parsers.rst.directives.admonitions import Hint
from docutils import nodes
from docutils.statemachine import StringList


def setup_module(module):
    # Prevent nosetests trying to run setup function
    pass


class mpl_hint(nodes.hint):
    """ Node signals presence of MPL interactive block """


class MPLInteractive(Hint):
    """ Output information on IPython / MPL interactive mode in Sphinx
    """

    node_class = mpl_hint

    default_text = """\
If running in the IPython console, consider running ``%matplotlib`` to enable
interactive plots.  If running in the Jupyter Notebook, use ``%matplotlib
inline``.
"""

    def run(self):
        if len(self.content) == 0:
            self.content = StringList(self.default_text.splitlines())
        return super(MPLInteractive, self).run()


def visit_mpl_inter(self, node):
    self.visit_hint(node)


def depart_mpl_inter(self, node):
    self.depart_hint(node)


def setup(app):
    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir

    # mpl_hint treated same as hint
    app.add_node(mpl_hint,
                 **{builder: (visit_mpl_inter, depart_mpl_inter)
                    for builder in ('html', 'latex', 'text')})
    app.add_directive('mpl-interactive', MPLInteractive)
