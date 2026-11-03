import json
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import requests
from data_source import normalize, filter_records, website_url, email_url, load_records

class DirectoryTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads(Path(__file__).with_name('data_snapshot.json').read_text())
        self.rows = [normalize(row) for row in self.raw]

    def test_snapshot_and_status_counts(self):
        self.assertEqual(len(self.rows), 88)
        self.assertEqual(sum(row['status'] == 'Active' for row in self.rows), 49)
        self.assertEqual(len({d for row in self.rows for d in row['districts']}), 11)

    def test_combined_filters(self):
        matches = filter_records(self.rows, 'acres', 'B', 'Active')
        self.assertEqual([row['name'] for row in matches], ['Acres Homes'])
        self.assertEqual(filter_records(self.rows, 'acres', 'A'), [])
        self.assertTrue(any(row['number'] == '23' for row in filter_records(self.rows, '23')))

    def test_link_cleanup(self):
        self.assertEqual(website_url(' facebook.com/groups/123 '), 'https://facebook.com/groups/123')
        self.assertEqual(website_url('example.org'), 'https://example.org')
        self.assertIsNone(website_url('javascript:alert(1)'))
        self.assertIsNone(website_url('https://example.org@evil.org/path'))
        self.assertIsNone(website_url(''))
        self.assertEqual(email_url('a@example.org, b@example.org;'), 'mailto:a@example.org,b@example.org')
        self.assertIsNone(email_url('not provided'))
        self.assertEqual(normalize({'Meeting Type':';#In Person;#'})['format'], 'In Person')

    @patch('data_source.requests.get')
    def test_live_paging(self, get):
        first, second = Mock(), Mock()
        first.json.return_value = {'success':True, 'result':{'records':self.raw[:40], 'total':88}}
        second.json.return_value = {'success':True, 'result':{'records':self.raw[40:], 'total':88}}
        get.side_effect = [first, second]
        rows, fallback = load_records()
        self.assertEqual(len(rows), 88)
        self.assertFalse(fallback)
        self.assertEqual(get.call_args_list[1].kwargs['params']['offset'], 40)

    @patch('data_source.requests.get', side_effect=requests.Timeout())
    def test_outage_uses_snapshot(self, get):
        rows, fallback = load_records()
        self.assertTrue(fallback)
        self.assertEqual(len(rows), 88)

if __name__ == '__main__':
    unittest.main()
