import unittest
from unittest.mock import Mock

from server.core.rules.matching.rules import (do_paths_match, do_cookies_match, do_methods_match, do_headers_match,
                                              do_queries_match)


class MatchRulesTest(unittest.TestCase):

    def test_do_paths_match(self):
        test_cases = [
            (True, 'matching_path', 'matching_path'),
            (False, 'matching_path', 'non_matching_path')
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(path=test_case[1])
                request = Mock(path=test_case[2])

                actual = do_paths_match(None, entry, request)

                self.assertEqual(test_case[0], actual)

    def test_do_cookies_match(self):
        test_cases = [
            (True, {}, {}),
            (True, {'matching-name': 'matching-value'}, {'matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {}),
            (False, {'matching-name': 'matching-value'}, {'non-matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {'matching-name': 'non-matching-value'})
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(cookies=test_case[1])
                request = Mock(cookies=test_case[2])

                actual = do_cookies_match(None, request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_methods_match(self):
        test_cases = [
            (True, 'GET', 'GET'),
            (False, 'GET', 'POST')
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(method=test_case[1])
                request = Mock(method=test_case[2])

                actual = do_methods_match(None, request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_headers_match(self):
        test_cases = [
            (True, {}, {}),
            (True, {'matching-name': 'matching-value'}, {'matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {}),
            (False, {'matching-name': 'matching-value'}, {'non-matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {'matching-name': 'non-matching-value'})
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(headers=test_case[1])
                request = Mock(headers=test_case[2])

                actual = do_headers_match(None, request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_query_params_match(self):
        test_cases = [
            (True, {}, {}),
            (True, {'matching-name': 'matching-value'}, {'matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {}),
            (False, {'matching-name': 'matching-value'}, {'non-matching-name': 'matching-value'}),
            (False, {'matching-name': 'matching-value'}, {'matching-name': 'non-matching-value'})
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(query_params=test_case[1])
                request = Mock(query_params=test_case[2])

                actual = do_queries_match(None, request, entry)

                self.assertEqual(test_case[0], actual)
