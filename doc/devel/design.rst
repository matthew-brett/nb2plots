###########################
Design of a notebook writer
###########################

Pages that will be converted to notebooks have, somewhere in them, of one of
these forms::

    :clearnotebook:``
    :fullnotebook:``

These generate page content equivalent to ``:download:`<pagename>.ipynb```,
where ``<pagename>.rst`` is the name of the ReST page containing the notebook
role.  ``:clearnotebook:`` creates a notebook without outputs, and
``:fullnotebook:`` creates the notebook and executes it, writing the notebook
with generated outputs.

For both directives, you can replace the default link text by adding link
text::

    :clearnotebook:`to get this page as an ipynb file`

You can specify the written filename of the notebook with the ``text
<target>`` form of the role::

    :clearnotebook:`to get this page as an ipynb file <my_nb.ipynb>`

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
