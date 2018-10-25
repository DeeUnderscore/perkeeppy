# -*- coding: utf-8 -*-


class ConnectionError(Exception):
    """
    There was some kind of error while establishing an initial connection
    to a Perkeep server.
    """
    pass


class NotPerkeepServerError(ConnectionError):
    """
    When attempting to connect to a Perkeep server it was determined that
    the given resource does not implement the Perkeep protocol, and is
    thus assumed not to be a Perkeep server.
    """
    pass


class NotFoundError(Exception):
    """
    The requested object was not found on the server.
    """
    pass


class ServerError(Exception):
    """
    The server returned an unexpected error in response to some operation.
    """
    pass


class ServerFeatureUnavailableError(Exception):
    """
    The server does not implement the requested feature.

    This can occur if
    e.g. a particular server is running a blob store but is not running
    an indexer, and a caller tries to use search features.
    """
    pass


class HashMismatchError(Exception):
    """
    There was a mismatch between an expected hash value an an actual hash
    value.
    """
    pass


class SigningError(Exception):
    """
    There was a problem with cryptographically signing a JSON blob.
    """
