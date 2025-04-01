from typing import Dict
from pathlib import Path

import unittest

from server.core.config import set_root_path, get_root_path
from server.core.har import HarParser, HarEntryRequest, HarEntryResponse


class HarParserTest(unittest.TestCase):
    
    def test_get_har_file_contents(self):
        test_har_path = (Path(__file__)
                         .parent
                         .parent
                         .joinpath('integration')
                         .joinpath('test_data')
                         .joinpath('request_matching'))
        if not test_har_path.is_dir():
            raise ValueError(f'Could not find test data dir in expected location of: [{test_har_path}]')

        previous_path = get_root_path()

        try:

            set_root_path(test_har_path)

            parser = HarParser()
            har_file_contents = parser.get_har_file_contents()

            self.assertIsNotNone(har_file_contents)
            self.assertEqual(1, len(har_file_contents))
            self.assertEqual(1, len(har_file_contents[0].entries))

            self._assert_request(har_file_contents[0].entries[0].request)

            self._assert_response(har_file_contents[0].entries[0].response)

        finally:
            set_root_path(previous_path)
    
    def _assert_request(self, request: HarEntryRequest):
        self.assertIsNotNone(request)

        headers = request.headers
        self._assert_has_entries({
            "request-header-name": "request-header-value",
            "content-type": "application/json"
        }, headers)

        cookies = request.cookies
        self._assert_has_entries({
            "request-cookie-name": "request-cookie-value"
        }, cookies)

        query_params = request.query_params
        self._assert_has_entries({
            "query-param-name": "query-param-value"
        }, query_params)

        request_body = request.body
        self.assertIsNotNone(request_body)

        request_body_name = request_body.get('name')
        self.assertEqual('test_name', request_body_name)

        request_body_password = request_body.get('password')
        self.assertEqual('test_password', request_body_password)

    def _assert_response(self, response: HarEntryResponse):
        self.assertIsNotNone(response)
    
    def _assert_has_entries(self, expected: Dict[str, str], actual: Dict[str, str]):
        self.assertIsNotNone(actual)
        self.assertEqual(len(expected), len(actual))
        for key, value in expected.items():
            self._assert_has_entry(key, value, actual)

    def _assert_has_entry(self, name: str, value: str, entries: Dict[str, str]):
        entry_value = entries.get(name)
        self.assertIsNotNone(entry_value, f'Expected dict to contain entry with key [{name}]')
        self.assertEqual(entry_value, value, f'Expected entry [{name}] to have a value of [{value}].')
