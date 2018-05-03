import unittest
import requests
import requests_mock
from requests_toolbelt.multipart.decoder import MultipartDecoder
import io

from perkeeppy.uploadhelper import UploadHelper


class UploadHelperTest(unittest.TestCase):
    def setUp(self):
        self.http_sess = requests.session()
        self.uploadhelper = UploadHelper(self.http_sess,
                                         'https://example.com/perkeep/')

    def test_uploadhelper(self):
        file = io.BytesIO(b"I'm a file, yes I am!")
        response = ('{"got":[{"filename":"afile",'
                    '"fileref":"sha224-aaaabbbb"}]}')

        mock = requests_mock.Mocker()
        mock.post('https://example.com/perkeep/', text=response)

        with mock:
            fileref = self.uploadhelper.upload_file('afile', file,
                                                    '2010-01-02T10:20:30Z')

        self.assertEqual(fileref, 'sha224-aaaabbbb')

        decoder = MultipartDecoder(mock.last_request.body,
                                   mock.last_request.headers['Content-Type'])

        found_modtime, found_file = False, False

        for part in decoder.parts:
            if b'modtime' in part.headers[b'Content-Disposition']:
                self.assertEqual(part.content, b'2010-01-02T10:20:30Z')
                found_modtime = True

            elif b'afile' in part.headers[b'Content-Disposition']:
                self.assertEqual(part.content, b"I'm a file, yes I am!")
                found_file = True

        self.assertTrue(found_modtime,
                        'modtime was not found in multipart data')
        self.assertTrue(found_file,
                        'file was not found in multipart data')
