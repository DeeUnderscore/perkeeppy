Accessing the Blob Store
========================

The lowest-level interface in Perkeep is the raw blob store, which provides
a mechanism to store and retrieve immutable objects. All other Perkeep
functionality is built on this base layer.

Blob store functionality is accessed via
:py:attr:`perkeeppy.Connection.blobs`, which is a pre-configured instance
of :py:class:`perkeeppy.blobclient.BlobClient`.

.. autoclass:: perkeeppy.blobclient.BlobClient
   :members:

.. autoclass:: perkeeppy.Blob
   :members:

.. autoclass:: perkeeppy.blobclient.BlobMeta
   :members:
