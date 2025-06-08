from typing import List, Tuple, Dict
import unittest
from unittest.mock import Mock

from server.core.rules.matching.rules import (
    PathMatcherRule,
    CookieMatcherRule,
    MethodMatcherRule,
    HeadersMatcherRule,
    QueryMatcherRule,
    BodyMatcherRule
)


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

                actual = PathMatcherRule().matches(entry, request)

                self.assertEqual(test_case[0], actual)

    def test_do_cookies_match(self):
        test_cases: List[Tuple[bool, Dict[str, str], Dict[str, str]]] = [
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

                actual = CookieMatcherRule().matches(request, entry)

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

                actual = MethodMatcherRule().matches(request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_headers_match(self):
        test_cases: List[Tuple[bool, Dict[str, str], Dict[str, str]]] = [
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

                actual = HeadersMatcherRule().matches(request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_query_params_match(self):
        test_cases: List[Tuple[bool, Dict[str, str], Dict[str, str]]] = [
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

                actual = QueryMatcherRule().matches(request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_bodies_match(self):
        test_cases: List[Tuple[bool, Dict[str, str] | None, Dict[str, str] | None]] = [
            (True, {}, {}),
            (True, None, None),
            (False, None, {}),
            (False, {}, None),
            (False, {}, {'name': 'name'})
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(body=test_case[1])
                request = Mock(body=test_case[2])

                actual = BodyMatcherRule().matches(request, entry)

                self.assertEqual(test_case[0], actual)
