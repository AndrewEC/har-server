from typing import List, Tuple, Dict
import unittest
from unittest.mock import Mock

from server.core.har.models import NameValuePair
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
            (False, 'matching_path', 'non_matching_path'),
            (True, '/user/*/address', '/user/23/address'),
            (True, '/user/*/address', '/user/23/address'),
            (False, '/user/*/address', '/user/23/addres'),
            (False, '/user/*/address', '/user/address')
        ]

        for test_case in test_cases:
            with self.subTest(should_match=test_case[0]):
                entry = Mock(path=test_case[1])
                request = Mock(path=test_case[2])

                matcher = PathMatcherRule()
                matcher.initialize(Mock())
                actual = matcher.matches(entry, request)

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
                entry = Mock(cookies=self._to_name_value_pairs(test_case[1]))
                request = Mock(cookies=self._to_name_value_pairs(test_case[2]))

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
                entry = Mock(headers=self._to_name_value_pairs(test_case[1]))
                request = Mock(headers=self._to_name_value_pairs(test_case[2]))

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
                entry = Mock(query_params=self._to_name_value_pairs(test_case[1]))
                request = Mock(query_params=self._to_name_value_pairs(test_case[2]))

                actual = QueryMatcherRule().matches(request, entry)

                self.assertEqual(test_case[0], actual)

    def test_do_json_bodies_match(self):
        entry = Mock(post_data = Mock(
            mime_type='application/json',
            parsed_json={'test':'value'}
        ))

        actual = BodyMatcherRule().matches(entry, entry)

        self.assertTrue(actual)
    
    def test_do_form_url_encoded_bodies_match(self):
        entry = Mock(post_data = Mock(
            mime_type='application/x-www-form-urlencoded',
            params=[
                NameValuePair(name='test', value='value')
            ]
        ))

        actual = BodyMatcherRule().matches(entry, entry)

        self.assertTrue(actual)

    def _to_name_value_pairs(self, entries: Dict[str, str]) -> List[NameValuePair]:
        return [NameValuePair(name=key, value=value) for key, value in entries.items()]
