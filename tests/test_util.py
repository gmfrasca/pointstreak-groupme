import unittest
from unittest import mock
from psgroupme.util.encode_strings import encode_strings
from psgroupme.util.parsetime import normalize_date, normalize_time, assemble_full_datetime
import datetime

class TestEncodeStrings(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_encode_strings(self):
        self.assertEqual(encode_strings('test'), 'test')
        self.assertEqual(encode_strings(['test', 'test2']), ['test', 'test2'])
        self.assertEqual(encode_strings({'test': 'test2'}), {'test': 'test2'})
        self.assertEqual(encode_strings(1), 1)
        self.assertEqual(encode_strings(1.0), 1.0)
        self.assertEqual(encode_strings(True), True)
        self.assertEqual(encode_strings(False), False)
        self.assertEqual(encode_strings(None), None)

    def test_encode_strings_with_nested_list(self):
        self.assertEqual(encode_strings([['test', 'test2'], ['test3', 'test4']]), [['test', 'test2'], ['test3', 'test4']])
        self.assertEqual(encode_strings([['test', 'test2'], ['test3', 'test4']]), [['test', 'test2'], ['test3', 'test4']])

    def test_encode_strings_with_nested_dict(self):
        self.assertEqual(encode_strings({'test': {'test2': 'test3'}}), {'test': {'test2': 'test3'}})
        self.assertEqual(encode_strings({'test': {'test2': 'test3'}}), {'test': {'test2': 'test3'}})

    def test_encode_strings_with_nested_list_and_dict(self):
        self.assertEqual(encode_strings([['test', 'test2'], {'test3': 'test4'}]), [['test', 'test2'], {'test3': 'test4'}])
        self.assertEqual(encode_strings([['test', 'test2'], {'test3': 'test4'}]), [['test', 'test2'], {'test3': 'test4'}])

    def test_encode_strings_with_nested_list_and_dict_and_list(self):
        self.assertEqual(encode_strings([['test', 'test2'], {'test3': 'test4'}, ['test5', 'test6']]), [['test', 'test2'], {'test3': 'test4'}, ['test5', 'test6']])
        self.assertEqual(encode_strings([['test', 'test2'], {'test3': 'test4'}, ['test5', 'test6']]), [['test', 'test2'], {'test3': 'test4'}, ['test5', 'test6']])

class TestParseTime(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_normalize_date(self):
        self.assertEqual(normalize_date('Wed, Aug 5'), 'Wed, Aug 05')

    def test_normalize_date_with_year(self):
        expected = datetime.datetime(2026, 8, 5)
        actual = normalize_date('Wed, Aug 5', year=2026, return_type=datetime.datetime)
        self.assertEqual(actual.year, expected.year)
        self.assertEqual(actual.month, expected.month)
        self.assertEqual(actual.day, expected.day)

    def test_normalize_date_with_includes_day(self):
        expected = datetime.datetime(2026, 8, 5)
        actual = normalize_date('Wed, Aug 5', includes_day=True, return_type=datetime.datetime)
        self.assertEqual(actual.year, expected.year)
        self.assertEqual(actual.month, expected.month)
        self.assertEqual(actual.day, expected.day)

    def test_normalize_date_with_return_type(self):
        expected = datetime.datetime(2026, 8, 5)
        actual = normalize_date('Wed, Aug 5', return_type=datetime.datetime)
        self.assertEqual(actual.year, expected.year)
        self.assertEqual(actual.month, expected.month)
        self.assertEqual(actual.day, expected.day)

    def test_normalize_date_with_includes_day_and_return_type(self):
        expected = datetime.datetime(2026, 8, 5)
        actual = normalize_date('Wed, Aug 5', includes_day=True, return_type=datetime.datetime)
        self.assertEqual(actual.year, expected.year)
        self.assertEqual(actual.month, expected.month)
        self.assertEqual(actual.day, expected.day)

    def test_normalize_time(self):
        self.assertEqual(normalize_time('8:45 PM'), '08:45 PM')

    def test_normalize_time_with_return_type(self):
        expected = datetime.datetime(2026, 8, 5, 20, 45)
        actual = normalize_time('8:45 PM', return_type=datetime.datetime)
        self.assertEqual(actual.hour, expected.hour)
        self.assertEqual(actual.minute, expected.minute)

    def test_assemble_full_datetime(self):
        self.assertEqual(assemble_full_datetime('Wed, Aug 5', '8:45 PM'), datetime.datetime(2026, 8, 5, 20, 45))