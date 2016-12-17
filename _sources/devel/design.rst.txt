###########################
Design of a notebook writer
###########################

Pages that will be converted to notebooks have, somewhere in them, one of two
intepreted text roles, like this::

    :clearnotebook:`Download as notebook without outputs`
    :fullnotebook:`Download as notebook with outputs`

These generate page content equivalent to ``:download:`Download as notebook
<pagename>.ipynb```, where ``<pagename>.rst`` is the name of the ReST page
containing the notebook role.  ``:clearnotebook:`` creates a notebook without
outputs, and ``:fullnotebook:`` creates the notebook and executes it, writing
the notebook with generated outputs.

The text within the backticks is the link text that will appear in the build
html, unless the text is ``.`` (a period).  This special case causes the link
text to be ``Download as IPython notebook``.

It appears that docutils insists that there must be some text between the
backticks.

For both directives, you can specify the written filename of the notebook with
the ``text <target>`` form of the role::

    :clearnotebook:`to get this page as an ipynb file <my_nb.ipynb>`

If you want to specify the filename, you must specify link text as well.  For
example ``:clearnotebook:`<my_nb.ipynb>``` will result in the default
filename, and a link text of ``<my_nb.ipynb>``.

You can have multiple notebook roles pointing to the same file (default or
otherwise), as long as they are all of the same type (clear or full).  For
example, you can have multiple ``:clearnotebook:`.``` roles in one ReST page,
(all pointing to ``<pagename>.ipynb``, but you cannot have a
``:fullnotebook:`.``` role in that page, because that would mean that the
clear and full notebook roles were trying to point to the same file.

*********
Mechanics
*********

On page parse (``doctree-resolved`` event), register that the page containing
the notebook role should generate notebook, and whether this should be "full"
or "clear".  Store in ``app.env``, with link to 

Either collect the doctrees in the ``doctree-resolved`` event, or collect the
docnames there, and then generate the notebooks in ``html-collect-pages``
event.

Add notebook vistor functions via ``app.add_node(clearnotebook,
html=(visit_notebook_node, depart_notebook_node)`` in ``setup`` function.

Maybe make a new ``Writer`` class to write the notebook from the doctree.
