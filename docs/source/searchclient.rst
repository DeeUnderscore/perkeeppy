Accessing the Search Interface
==============================

Most interesting functionality of Perkeep is implemented in terms of the search
interface, which is provided by Perkeep's indexer. It visits all of the stored
blobs and discovers higher-level relationships between them based on its
understanding of various schemas.

Search functionality is accessed via
:py:attr:`perkeeppy.Connection.searcher`, which is a pre-configured instance
of :py:class:`perkeeppy.searchclient.SearchClient`.

.. autoclass:: perkeeppy.searchclient.SearchClient
   :members:

Get Blob Descriptions
---------------------

One important feature of search interface is its ability to obtain the
current state of a mutable object, or even its state at a particular
point in time.

:py:meth:`perkeeppy.searchclient.SearchClient.describe_blob` takes a
blobref and returns a :py:class:`perkeeppy.searchclient.BlobDescription`
object that provides access to the index metadata for the given blob,
as well as efficient access to descriptions of related objects.

.. autoclass:: perkeeppy.searchclient.BlobDescription
   :members:

Execute Search Queries
----------------------

The other main capability of the search interface is querying the store
to find objects fitting certain criteria.

:py:attr:`perkeeppy.searchclient.SearchClient.query` is the interface
to this functionality, returning an iterable of
:py:class:`perkeeppy.searchclient.SearchResult` objects.

.. autoclass:: perkeeppy.searchclient.SearchResult
   :members:

Access Raw Permanode Claims
---------------------------

The mechanism by which Perkeep implements mutable objects is via
*permanodes* which act as an immitable persistent "name" for a mutable object,
and *claims* which describe mutations of permanodes.

Most callers will use the flattened list of permanode attributes provided
by :py:meth:`perkeeppy.searchclient.SearchClient.describe_blob`, but it
is also possible to access the raw claim list for a permanode via
:py:meth:`perkeeppy.searchclient.SearchClient.get_claims_for_permanode`,
which returns an iterable of :py:class:`perkeeppy.searchclient.ClaimMeta`
objects.

.. autoclass:: perkeeppy.searchclient.ClaimMeta
   :members:
