import unittest
import json
from datetime import datetime, timezone, timedelta

from unittest import mock

from camlistore.schema import SchemaObject, get_permanode, make_claim


class TestSchemaObject(unittest.TestCase):
    def test_defaults(self):
        schema_obj = SchemaObject('test')

        self.assertDictEqual(schema_obj.data,
                             {'camliType': 'test', 'camliVersion': 1})

    def test_unsigned_blob(self):
        desired = {'camliType': 'test',
                   'camliVersion': 1,
                   'hello': 'test'}

        schema_obj = SchemaObject('test', data={'hello': 'test'})

        blob = schema_obj.to_blob()

        parsed = json.loads(blob.data)

        self.assertDictEqual(parsed, desired)

    def test_signed_blob(self):
        schema_obj = SchemaObject('test', needs_signing=True)

        mock_signer = mock.MagicMock()
        mock_signer.sign_dict = mock.MagicMock(return_value=b'TESTPASSED')

        blob = schema_obj.to_blob(signer=mock_signer)

        self.assertEqual(blob.data, b'TESTPASSED')


class TestPermanode(unittest.TestCase):
    def test_permanode_generation(self):
        with mock.patch('camlistore.schema.SchemaObject') as mocked:
            permanode_obj = get_permanode()

        self.assertEqual(mocked.call_args[0][0], 'permanode')
        self.assertIn('random', mocked.call_args[1]['data'])
        self.assertTrue(mocked.call_args[1]['needs_signing'])

    def test_claim(self):
        with mock.patch('camlistore.schema.SchemaObject') as mocked:
            claim = make_claim('sha224-aaaa', 'test', 'set', True)

        self.assertEqual(mocked.call_args[0][0], 'claim')
        self.assertTrue(mocked.call_args[1]['needs_signing'])

        data = mocked.call_args[1]['data']

        desired = {'permaNode': 'sha224-aaaa',
                   'attribute': 'test',
                   'claimType': 'set-attribute',
                   'value': True}

        self.assertTrue(data.items() >= desired.items())

    def test_claim_errors(self):
        with self.assertRaises(ValueError):
            make_claim('sha224-aaa', 'test', 'flobble', True)

        with self.assertRaises(ValueError):
            make_claim('sha224-aaa', 'test', 'set', True, date=False)

    def test_claim_daes(self):
        naive = datetime(2010, 1, 2, 10, 20, 30)
        tzd = datetime(2010, 1, 2, 11, 20, 30,
                       tzinfo=timezone(timedelta(hours=1)))

        desired = datetime(2010, 1, 2, 10, 20, 30, tzinfo=timezone.utc)

        with mock.patch('camlistore.schema.SchemaObject') as mocked:
            make_claim('sha224-aaa', 'test', 'set', True, date=naive)

        date_received = mocked.call_args[1]['data']['claimDate']
        self.assertEqual(date_received, desired.isoformat())

        with mocked:
            make_claim('sha224-aaa', 'test', 'set', True, date=tzd)

        date_received = mocked.call_args[1]['data']['claimDate']
        self.assertEqual(date_received, desired.isoformat())
