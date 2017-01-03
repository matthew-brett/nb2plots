.. _links-in-markdown:

#################
Links in Markdown
#################

By default, if your ReST documents has internal links, then generated Markdown
output like the Notebook files or the Python code files drop these links,
replacing them with some suitable text.

Internal links can be :ref:`internal to the document <links-in-markdown>`, via
the ``:ref:`` role, or to :doc:`other ReST pages <scripts>`, using the
``:doc:`` role.  Links can also be to files to download, such as
:download:`conf.py`.

It's often the case that you have built HTTP pages on the web somewhere, so it
would make sense for the built Markdown to point to the HTTP versions of these
links, rather than dropping them.

You can tell ``nb2plots`` where your built HTTP docs are, by setting the
``markdown_http_base`` value in your ``conf.py`` file, like this::

    markdown_http_base = 'https://example.com'

If you set this value to any string other than the empty string, the Markdown
builders will use this base URL to resolve internal links.

In fact, I've set that option in the ``conf.py`` for this project, like this::

    markdown_http_base = 'https://matthew-brett.github.io/nb2plots'

Have a look at the generated Python code and Notebook code for this pages, via
the links below.  You should see that the Markdown links resolve to the HTTP
pages at https://matthew-brett.github.io/nb2plots.

.. code-links::
