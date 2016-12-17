""" Directive to handle ``%matplotlib [inline]`` in Sphinx, Notebooks

The directive is a marker to tell the Notebook converter to put a ``%matplotlib
inline`` code cell at this position in the text.  Use thusly::

    .. mpl-interactive::

With no content (as above), the directive inserts a Hint into the ReST text
suggesting ``%matplotlib`` in the IPython console, or ``%matplotlib inline`` in
the Notebook.  You can specify some other message with::

    .. mpl-interactive::

        Your text here.

The text can be any valid ReStructured text.
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
