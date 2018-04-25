import io


class UploadHelper(object):
    """
    An interface to the Perkeep upload helper.

    The upload helper endpoint allows for uploading of whole files into
    Perkeep, with automatic chunking and generation of a file schema blob. This
    allows ploading of files without the need to do chunking/span trees
    locally.
    """

    def __init__(self, http_session, base_url):
        self.http_session = http_session
        self.base_url = base_url

    def upload_file(self, filename, fileobj, mtime=None):
        """
        Upload a single file.

        ``filename`` is the desired file name to be stored in the blob store.
        It cannot be blank. ``fileobj`` is a file-like object containing the
        contents of the file to be stored. Optionally, ``mtime`` can also be a
        string with a valid file modification timestamp (meaning an ISO
        timestamp).

        Returns a blobref pointing to the schema object for the file.
        """

        if not filename or not isinstance(filename, str):
            raise ValueError(f'Invalid filename supplied: {filename}')

        # Perkeep does not actually (currently; 2018-04) care about the name
        # field, other than when it's 'modtime'
        payload = [('file', (filename, fileobj))]

        if mtime:
            # Requests wants a file-like object
            payload.append(('modtime', (None, mtime)))

        result = self.http_session.post(self.base_url, files=payload)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ServerError('Server returned a non-200 result.') from e

        return result.json()['got'][0]['fileref']
