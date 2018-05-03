from urllib.parse import urljoin
import requests
import json

from perkeeppy.exceptions import SigningError, ServerError

CAMLI_VERSION = 1


class Signer(object):
    """
    An interface to the Perkeep signing helper.

    In general, instances of this should be obtained from
    :attr:`perkeeppy.Connection.signer`

    ``base_url`` should include a trailing slash. ``camli_signer`` can,
    optionally, be a string with the blobref of the public key. If left out,
    it will be fetched via discovery the first time it is needed (or, if the
    ``camli_signer`` is assigned to `None` afterwards).
    """

    def __init__(self, http_session, base_url, camli_signer=None):
        self.http_session = http_session
        self.base_url = base_url

        # Note that the discovery (as well as the root discovery) JSON includes
        # paths for sign and verify, but the documentation also says they're at
        # fixed subpaths of signer root. As such, we don't fetch discovery here
        self.discovery_path = urljoin(self.base_url, 'camli/sig/discovery')
        self.sign_path = urljoin(self.base_url, 'camli/sig/sign')
        self.verify_path = urljoin(self.base_url, 'camli/sig/verify')

        self._camli_signer = camli_signer

    @property
    def camli_signer(self):
        if self._camli_signer:
            return self._camli_signer

        self._camli_signer = (self.http_session.get(self.discovery_path)
                                               .json()['publicKeyBlobRef'])

        return self._camli_signer

    @camli_signer.setter
    def camli_signer(self, newval):
        self._camli_signer = newval

    def sign_dict(self, source):
        """
        Produce a signed :class:`bytes` version of the ``source``.

        ``source`` does not have to have either a ``camliVersion``, nor a
        ``camliSigner`` field. They will be filled out as needed, with the
        ``camliSigner`` fetched from the API if not already cached.
        """

        if 'camliVersion' not in source:
            source['camliVersion'] = CAMLI_VERSION

        if 'camliSigner' not in source:
            source['camliSigner'] = self.camli_signer

        return self.sign_string(json.dumps(source))

    def sign_string(self, source):
        """
        Produce a signed :class:`bytes` version of the JSON string in
        ``source``.

        For a yet-unserialized dictionary, :meth:`sign_dict` is generally a
        better choice, as it will supply the mandatory JSON fields if they are
        not present. This method will not perform any checks on the input, but
        instead it will return a :class:`SigningError` if the remote returns an
        error, and attach the Requests exception as cause.

        Returns a :class:`bytes` object with the signed JSON
        """

        resp = self.http_session.post(self.sign_path, data={'json': source})

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SigningError from e

        return resp.content

    def verify_bytes(self, byte_str):
        """
        Use the remote signing helper to vefify a cryptographically signed JSON
        document.

        The ``byte_str`` should be of the :class:`bytes` type.

        The function will return a tuple: the first member will be either
        ``True`` or ``False``, depending on whether the signature was valid; if
        verification failed, the second member will be a string explaining why.

        The function may raise :class:`ServerError` in case of a server-side
        problem.
        """

        resp = self.http_session.post(self.verify_path,
                                      data={'sjson': byte_str})

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ServerError from e

        resp_json = resp.json()

        if resp_json['signatureValid']:
            return (True, None)
        else:
            return (False, resp_json['errorMessage'])
