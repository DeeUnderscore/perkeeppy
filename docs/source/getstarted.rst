Getting Started
===============

Install The Module
------------------

This is a standard Python module and can be installed using ``pip`` as usual:

* ``pip install .``

Connect To Perkeep
------------------

Before this library will be of any use you will need a Perkeep server running.
See `the Perkeep docs`_ for more details.

Once you have a server running you can connect to it using
:py:func:`perkeeppy.connect`. For example, if you have your Perkeep server 
running on localhost:

.. code-block:: python

    import perkeeppy

    conn = perkeeppy.connect("http://localhost:3179/")

This function will contact the specified URL to make sure it looks like
a valid Perkeep server and discover some details about its configuration. The 
``conn`` return value is then a :py:class:`perkeeppy.Connection` object, 
configured and ready to access the server.

.. _`the Perkeep docs`: https://perkeep.org/doc/

Try Writing A Blob!
-------------------

To test if we've connected successfully, we can try some simple calls to
write a blob and retrieve it again:

.. code-block:: python

    blobref = conn.blobs.put(perkeeppy.Blob(b"Hello, Perkeep!"))
    hello_blob = conn.blobs.get(blobref)
    print(hello_blob.data.decode())

If things are working as expected, this should print out
``Hello, Perkeep!``, having successfully written that string into the store
and retrieved it again. You're now ready to proceed to the following sections
to learn more about the blob store and search interfaces.

This program will fail if the connection is not configured properly. For
example, it may fail if the Perkeep server requires authentication, since
our example does not account for that.

Connection Interface Reference
------------------------------

.. autofunction:: perkeeppy.connect

.. autoclass:: perkeeppy.Connection
    :members:
