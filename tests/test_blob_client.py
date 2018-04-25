
import unittest
from unittest.mock import MagicMock

from camlistore.blobclient import BlobClient, BlobMeta, Blob


class TestBlobClient(unittest.TestCase):

    def test_url_building(self):
        http_session = MagicMock()
        blobs = BlobClient(
            http_session=http_session,
            base_url="http://example.com/dummy-blobs/",
        )
        self.assertEqual(
            blobs._make_blob_url('dummy-blobref'),
            'http://example.com/dummy-blobs/camli/dummy-blobref',
        )

    def test_unavailable(self):
        http_session = MagicMock()
        blobs = BlobClient(
            http_session=http_session,
            base_url=None,
        )
        from camlistore.exceptions import ServerFeatureUnavailableError
        self.assertRaises(
            ServerFeatureUnavailableError,
            lambda: blobs._make_blob_url('dummy-blobref'),
        )

    def test_get_success(self):
        http_session = MagicMock()
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = b'dummy blob'

        blobs = BlobClient(
            http_session,
            'http://example.com/blerbs/',
        )
        result = blobs.get('sha1-7928f34bd3263b86e67d11efff30d67fe7f3d176')

        http_session.get.assert_called_with(
            "http://example.com/blerbs/camli/"
            "sha1-7928f34bd3263b86e67d11efff30d67fe7f3d176"
        )
        self.assertEqual(
            type(result),
            Blob,
        )
        self.assertEqual(
            result.data,
            b'dummy blob',
        )

    def test_get_hash_mismatch(self):
        from camlistore.exceptions import HashMismatchError

        http_session = MagicMock()
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = b'dummy blob'

        blobs = BlobClient(
            http_session,
            'http://example.com/blerbs/',
        )
        self.assertRaises(
            HashMismatchError,
            lambda: blobs.get('sha1-dummyblobref'),
        )
        http_session.get.assert_called_with(
            "http://example.com/blerbs/camli/sha1-dummyblobref"
        )

    def test_get_not_found(self):
        http_session = MagicMock()
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 404
        response.content = 'not found'

        blobs = BlobClient(
            http_session,
            'http://example.com/blerbs/',
        )
        from camlistore.exceptions import NotFoundError
        self.assertRaises(
            NotFoundError,
            lambda: blobs.get('dummy-blobref'),
        )
        http_session.get.assert_called_with(
            "http://example.com/blerbs/camli/dummy-blobref"
        )

    def test_get_server_error(self):
        http_session = MagicMock()
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 500
        response.content = 'error'

        blobs = BlobClient(
            http_session,
            'http://example.com/blerbs/',
        )
        from camlistore.exceptions import ServerError
        self.assertRaises(
            ServerError,
            lambda: blobs.get('dummy-blobref'),
        )
        http_session.get.assert_called_with(
            "http://example.com/blerbs/camli/dummy-blobref"
        )

    def test_get_size_success(self):
        http_session = MagicMock()
        http_session.request = MagicMock()
        response = MagicMock()
        http_session.request.return_value = response

        response.status_code = 200
        response.headers = {
            'content-length': 5
        }

        blobs = BlobClient(
            http_session,
            'http://example.com/blerbs/',
        )
        result = blobs.get_size('dummy-blobref')

        http_session.request.assert_called_with(
            "HEAD", "http://example.com/blerbs/camli/dummy-blobref"
        )
        self.assertEqual(
            result,
            5,
        )

    def test_blob_exists(self):
        http_session = MagicMock()

        class MockBlobClient(BlobClient):
            get_size = MagicMock()

        MockBlobClient.get_size.return_value = 12

        blobs = MockBlobClient(http_session, 'baz')
        result = blobs.blob_exists('foo')

        self.assertEqual(
            result,
            True,
        )
        MockBlobClient.get_size.assert_called_with(
            'foo',
        )

        from camlistore.exceptions import NotFoundError
        MockBlobClient.get_size.side_effect = NotFoundError('dummy')

        result = blobs.blob_exists('foo')
        self.assertEqual(
            result,
            False,
        )

    def test_enumerate(self):
        http_session = MagicMock()
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = """
        {
            "blobs": [
                {
                    "blobRef": "dummy1",
                    "size": 5
                },
                {
                    "blobRef": "dummy2",
                    "size": 9
                }
            ],
            "continueAfter": "dummy2"
        }
        """

        blobs = BlobClient(http_session, 'http://example.com/')
        iterable = blobs.enumerate()
        iterator = iterable.__iter__()

        blob_metas = []
        blob_metas.append(next(iterator))
        blob_metas.append(next(iterator))

        http_session.get.assert_called_with(
            'http://example.com/camli/enumerate-blobs'
        )

        # now set up for the second request
        http_session.get = MagicMock()
        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = """
        {
            "blobs": [
                {
                    "blobRef": "dummy3",
                    "size": 17
                }
            ]
        }
        """

        blob_metas.append(next(iterator))

        self.assertRaises(
            StopIteration,
            lambda: next(iterator),
        )

        self.assertEqual(
            [type(x) for x in blob_metas],
            [BlobMeta, BlobMeta, BlobMeta],
        )
        self.assertEqual(
            [x.blobref for x in blob_metas],
            ["dummy1", "dummy2", "dummy3"],
        )
        self.assertEqual(
            [x.size for x in blob_metas],
            [5, 9, 17],
        )

    def test_get_size_multi(self):
        http_session = MagicMock()
        http_session.post = MagicMock()
        response = MagicMock()
        http_session.post.return_value = response

        response.status_code = 200
        response.content = """
        {
            "stat": [
                {
                    "blobRef": "dummy1",
                    "size": 5
                },
                {
                    "blobRef": "dummy2",
                    "size": 9
                }
            ]
        }
        """

        blobs = BlobClient(http_session, 'http://example.com/')
        result = blobs.get_size_multi("dummy1", "dummy2")

        http_session.post.assert_called_with(
            "http://example.com/camli/stat",
            data={
                "camliversion": "1",
                "blob1": "dummy1",
                "blob2": "dummy2",
            },
        )

        self.assertEqual(
            result,
            {
                "dummy1": 5,
                "dummy2": 9,
            }
        )

    def test_put_multi(self):
        http_session = MagicMock()

        class MockBlobClient(BlobClient):
            get_size_multi = MagicMock()

        http_session.post = MagicMock()
        response = MagicMock()
        http_session.post.return_value = response

        response.status_code = 200

        MockBlobClient.get_size_multi.return_value = {
            ("sha224-"
             "5390db278c2643999c8aa539d9cc8b587e89bdbb289c4aff97971ccf"): 6,
            ("sha224-"
             "5d0307b0baad2ce34aab7cac92a3d72c57ca962ffad1dd365002d45e"): 6,
            ("sha224-"
             "f8d2cbd0991675d4e30fe52fff2b3bd00bdbfccc189c8c2e0fad4718"): None,
        }

        blobs = MockBlobClient(http_session, 'http://example.com/')
        result = blobs.put_multi(
            Blob(b"dummy1"),
            Blob(b"dummy2"),
            Blob(b"dummy3"),
        )

        MockBlobClient.get_size_multi.assert_called_with(
            'sha224-5390db278c2643999c8aa539d9cc8b587e89bdbb289c4aff97971ccf',
            'sha224-5d0307b0baad2ce34aab7cac92a3d72c57ca962ffad1dd365002d45e',
            'sha224-f8d2cbd0991675d4e30fe52fff2b3bd00bdbfccc189c8c2e0fad4718',
        )

        http_session.post.assert_called_with(
            "http://example.com/camli/upload",
            files={
                ('sha224-'
                 'f8d2cbd0991675d4e30fe52fff2b3bd00bdbfccc189c8c2e0fad4718'): (
                    ('sha224-f8d2cbd0991675d4e30fe5'
                     '2fff2b3bd00bdbfccc189c8c2e0fad4718'),
                    b'dummy3',
                    'application/octet-stream',
                )
            }
        )

        self.assertEqual(
            result,
            [
                ('sha224-'
                 '5390db278c2643999c8aa539d9cc8b587e89bdbb289c4aff97971ccf'),
                ('sha224-'
                 '5d0307b0baad2ce34aab7cac92a3d72c57ca962ffad1dd365002d45e'),
                ('sha224-'
                 'f8d2cbd0991675d4e30fe52fff2b3bd00bdbfccc189c8c2e0fad4718'),
            ]
        )


class TestBlob(unittest.TestCase):

    def test_instantiate(self):
        # TODO: Check for sha224 agreeing, too
        blob = Blob(b'hello',)
        self.assertEqual(
            blob.hash_func_name,
            'sha224',
        )
        self.assertEqual(
            blob.data,
            b'hello',
        )
        self.assertEqual(
            blob.blobref,
            'sha224-ea09ae9cc6768c50fcee903ed054556e5bfc8347907f12598aa24193',
        )

    def test_instantiate_different_hash(self):
        blob = Blob(b'hello', hash_func_name='sha256')
        self.assertEqual(
            blob.hash_func_name,
            'sha256',
        )
        self.assertEqual(
            blob.data,
            b'hello',
        )
        self.assertEqual(
            blob.blobref,
            'sha256-'
            '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824',
        )

    def test_change_hash_func(self):
        blob = Blob(b'hello')
        self.assertEqual(
            blob.blobref,
            'sha224-ea09ae9cc6768c50fcee903ed054556e5bfc8347907f12598aa24193',
        )
        blob.hash_func_name = 'sha1'
        self.assertEqual(
            blob.blobref,
            'sha1-aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d'
        )

    def test_change_data(self):
        blob = Blob(b'hello')
        self.assertEqual(
            blob.blobref,
            'sha224-ea09ae9cc6768c50fcee903ed054556e5bfc8347907f12598aa24193',
        )
        blob.data = b'world'
        self.assertEqual(
            blob.blobref,
            'sha224-06d2dbdb71973e31e4f1df3d7001fa7de268aa72fcb1f6f9ea37e0e5',
        )

    def test_string_data(self):
        self.assertRaises(
            TypeError,
            lambda: Blob('hello'),
        )

        blob = Blob(b'hello')

        def change_data():
            blob.data = 'hello'

        self.assertRaises(
            TypeError,
            change_data,
        )

    def test_func_name_as_func(self):
        import hashlib

        # must pass a function name, not a function
        # (we need the name so we can make the blobref prefix)
        self.assertRaises(
            TypeError,
            lambda: Blob('hello', hashlib.sha1),
        )
