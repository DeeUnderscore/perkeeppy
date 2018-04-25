import unittest
import requests
import requests_mock
import json
from urllib.parse import parse_qs

from camlistore.signing import Signer
from camlistore.exceptions import SigningError


class TestSigner(unittest.TestCase):

    def setUp(self):
        self.http_sess = requests.session()
        self.signer = Signer(self.http_sess, 'https://example.com/perkeep/')

    def test_instantiation(self):
        self.assertEqual(self.signer.discovery_path,
                         'https://example.com/perkeep/camli/sig/discovery')

        self.assertEqual(self.signer.sign_path,
                         'https://example.com/perkeep/camli/sig/sign')

        self.assertEqual(self.signer.verify_path,
                         'https://example.com/perkeep/camli/sig/verify')

    def test_camli_signer(self):
        ret = '{ "publicKeyBlobRef": "sha1-aaaabbbbccccdddd" }'

        mock = requests_mock.Mocker()

        # We need to use a valid URL here, since urljoin won't work otherwise.
        mock.get('https://example.com/perkeep/camli/sig/discovery', text=ret)
        signer = Signer(self.http_sess, 'https://example.com/perkeep/')

        with mock:
            # Straight up call to fetch
            self.assertEqual(self.signer.camli_signer, 'sha1-aaaabbbbccccdddd')

        # Manual assign
        signer.camli_signer = 'sha1-ffffeeeeffffeeee'

        self.assertEqual(signer.camli_signer, 'sha1-ffffeeeeffffeeee')

        # Refetch after assigning None
        self.signer.camli_signer = None

        with mock:
            self.assertEqual(self.signer.camli_signer, 'sha1-aaaabbbbccccdddd')

        self.assertEqual(mock.call_count, 2)  # since we refetched

    def test_json_string_signing(self):

        in_str = ('{\n\t"camliVersion": 1,\n'
                  '\t"camliSigner": "sha1-aaaabbbbccccdddd",\n'
                  '\t"someOtherData": "Hello"\n}')

        out_str = (b'{\n\t"camliVersion": 1,\n'
                   b'\t"camliSigner": "sha1-aaaabbbbccccdddd",\n'
                   b'\t"someOtherData": "Hello"\n}'
                   b',"camliSig":"AAABBB"}')

        mock = requests_mock.Mocker()
        mock.post('https://example.com/perkeep/camli/sig/sign',
                  content=out_str)

        with mock:
            result = self.signer.sign_string(in_str)

        # requests_mock theoretically has a .qs to do this for us, but calling
        # parse_qs this way seems to work better
        in_dict = parse_qs(mock.last_request.text)
        self.assertIn('json', in_dict)

        self.assertDictEqual(json.loads(in_dict['json'][0]),
                             json.loads(in_str))

        self.assertEqual(out_str, result)

    def test_dict_signing(self):
        in_dict = {"camliVersion": 1,
                   "camliSigner": "sha1-aaaabbbbccccdddd",
                   "someOtherData": "Hello"}

        out_str = (b'{\n\t"camliVersion": 1,\n'
                   b'\t"camliSigner": "sha1-aaaabbbbccccdddd",\n'
                   b'\t"someOtherData": "Hello"\n'
                   b',"camliSig":"AAABBB"}')

        mock = requests_mock.Mocker()
        mock.post('https://example.com/perkeep/camli/sig/sign',
                  content=out_str)

        with mock:
            result = self.signer.sign_dict(in_dict)

        posted_dict = parse_qs(mock.last_request.text)
        self.assertIn('json', posted_dict)
        self.assertDictEqual(json.loads(posted_dict['json'][0]), in_dict)

        self.assertEqual(out_str, result)

    def test_signing_throw_error(self):
        mock = requests_mock.Mocker()
        mock.post('https://example.com/perkeep/camli/sig/sign',
                  text='something is broken',
                  status_code=400)

        with mock:
            with self.assertRaises(SigningError) as cm:
                self.signer.sign_string(b'obviously wrong')

        self.assertIsInstance(cm.exception.__cause__,
                              requests.exceptions.HTTPError)

    def test_verification_valid(self):
        mock = requests_mock.Mocker()

        # note that real responses include more stuff, but Signer never
        # interacts with it
        mock.post('https://example.com/perkeep/camli/sig/verify',
                  text='{"signatureValid": true}')

        with mock:
            verified = self.signer.verify_bytes(b'{"pretendValidJson": true}')

        self.assertTupleEqual(verified, (True, None))

    def test_verification_invalid(self):
        mock = requests_mock.Mocker()

        mock.post('https://example.com/perkeep/camli/sig/verify',
                  text='{"signatureValid": false,'
                       '"errorMessage": "Obvious fake!"}')

        with mock:
            verified = self.signer.verify_bytes(b'{"pretendValidJson": false}')

        self.assertTupleEqual(verified, (False, 'Obvious fake!'))
