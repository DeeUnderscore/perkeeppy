
import unittest
from unittest.mock import MagicMock

from camlistore.searchclient import (
    SearchClient,
    ClaimMeta,
    SearchResult,
    BlobDescription,
)


class TestSearchClient(unittest.TestCase):

    def test_query(self):
        http_session = MagicMock()
        http_session.post = MagicMock()

        response = MagicMock()
        http_session.post.return_value = response

        response.status_code = 200
        response.content = """
        {
            "blobs": [
                {
                    "blob": "dummy-1"
                },
                {
                    "blob": "dummy-2"
                }
            ]
        }
        """

        searcher = SearchClient(
            http_session=http_session,
            base_url="http://example.com/s/",
        )

        results = searcher.query('dummyquery')

        http_session.post.assert_called_with(
            'http://example.com/s/camli/search/query',
            data='{"expression": "dummyquery"}',
        )

        self.assertEqual(
            [type(result) for result in results],
            [SearchResult, SearchResult],
        )
        self.assertEqual(
            [result.blobref for result in results],
            ["dummy-1", "dummy-2"],
        )

    def test_describe_blob(self):
        http_session = MagicMock()
        http_session.get = MagicMock()

        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = """
        {
            "meta": {
                "dummy1": {
                    "blobRef": "dummy1"
                },
                "dummy2": {
                    "blobRef": "dummy2"
                }
            }
        }
        """

        searcher = SearchClient(
            http_session=http_session,
            base_url="http://example.com/s/",
        )

        result = searcher.describe_blob("dummy1")

        http_session.get.assert_called_with(
            'http://example.com/s/camli/search/describe',
            params={
                'blobref': 'dummy1',
            }
        )

        self.assertEqual(
            type(result),
            BlobDescription,
        )

        self.assertEqual(
            result.raw_dict,
            {
                "blobRef": "dummy1",
            }
        )
        self.assertEqual(
            result.other_raw_dicts,
            {
                "dummy1": {
                    "blobRef": "dummy1",
                },
                "dummy2": {
                    "blobRef": "dummy2",
                },
            }
        )

    def test_get_claims_for_permanode(self):
        http_session = MagicMock()
        http_session.get = MagicMock()

        response = MagicMock()
        http_session.get.return_value = response

        response.status_code = 200
        response.content = """
        {
            "claims": [
                {
                    "dummy": 1
                },
                {
                    "dummy": 2
                }
            ]
        }
        """

        searcher = SearchClient(
            http_session=http_session,
            base_url="http://example.com/s/",
        )

        claims = searcher.get_claims_for_permanode('dummy1')

        http_session.get.assert_called_with(
            'http://example.com/s/camli/search/claims',
            params={
                "permanode": "dummy1",
            },
        )

        self.assertEqual(
            [type(claim) for claim in claims],
            [ClaimMeta, ClaimMeta],
        )
        self.assertEqual(
            [claim.raw_dict["dummy"] for claim in claims],
            [1, 2],
        )


class TestClaimMeta(unittest.TestCase):

    def test_attrs(self):
        from dateutil.tz import tzutc
        from datetime import datetime

        raw_dict = {
            "blobref": "dummy-blobref",
            "signer": "dummy-signer",
            "permanode": "dummy-permanode",
            "date": "2013-02-13T12:32:34.123Z",
            "type": "dummy-type",
            "attr": "dummy-attr",
            "value": 12,  # to make sure this doesn't get coerced to string
            "target": "dummy-target",
        }
        claim_meta = ClaimMeta(raw_dict)

        self.assertEqual(
            claim_meta.blobref,
            "dummy-blobref",
        )
        self.assertEqual(
            claim_meta.signer_blobref,
            "dummy-signer",
        )
        self.assertEqual(
            claim_meta.permanode_blobref,
            "dummy-permanode",
        )
        self.assertEqual(
            claim_meta.time,
            datetime(
                2013, 2, 13, 12, 32, 34, 123000, tzinfo=tzutc(),
            ),
        )
        self.assertEqual(
            claim_meta.type,
            "dummy-type",
        )
        self.assertEqual(
            claim_meta.attr,
            "dummy-attr",
        )
        self.assertEqual(
            claim_meta.value,
            12,
        )
        self.assertEqual(
            type(claim_meta.value),
            int,
        )
        self.assertEqual(
            claim_meta.target_blobref,
            "dummy-target",
        )


class TestBlobDescription(unittest.TestCase):

    def test_describe_another(self):
        searcher = MagicMock()
        descr = BlobDescription(
            searcher,
            {},
            other_raw_dicts={
                "baz": {
                    "blobRef": "baz"
                }
            }
        )

        searcher.describe_blob.return_value = "dummy-other"

        baz = descr.describe_another("baz")
        other = descr.describe_another("other")

        self.assertEqual(
            baz.blobref,
            "baz"
        )
        self.assertEqual(
            other,
            "dummy-other",
        )

        searcher.describe_blob.assert_called_with(
            "other",
        )
