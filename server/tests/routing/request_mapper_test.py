import unittest
from unittest.mock import AsyncMock

from server.core.routing.request_mapper import RequestMapper


class RequestMapperTest(unittest.IsolatedAsyncioTestCase):

    async def test_map_to_har_request_with_json_body(self):
        request = AsyncMock(
            query_params={'query_param_name': 'query_param_value'},
            headers={'header_name': 'header_value', 'content-type': 'application/json'},
            cookies={'cookie_name': 'cookie_value'},
            url='http://www.test.com',
            method='POST',
            body=AsyncMock(return_value=b'{"name":"Jason"}')
        )

        actual = await RequestMapper().map_to_har_request(request)

        self.assertEqual(request.query_params, actual.query_params)
        self.assertEqual(request.headers, actual.headers)
        self.assertEqual(request.cookies, actual.cookies)
        self.assertEqual(request.url, actual.url)
        self.assertEqual(request.method, actual.method)
        self.assertEqual({'name': 'Jason'}, actual.body)
    
    async def test_map_to_har_request_with_form_url_encoded_body(self):
        request = AsyncMock(
            query_params={'query_param_name': 'query_param_value'},
            headers={'header_name': 'header_value', 'content-type': 'application/x-www-form-urlencoded'},
            cookies={'cookie_name': 'cookie_value'},
            url='http://www.test.com',
            method='POST',
            body=AsyncMock(return_value=b'name=Jason')
        )

        actual = await RequestMapper().map_to_har_request(request)

        self.assertEqual(request.query_params, actual.query_params)
        self.assertEqual(request.headers, actual.headers)
        self.assertEqual(request.cookies, actual.cookies)
        self.assertEqual(request.url, actual.url)
        self.assertEqual(request.method, actual.method)
        self.assertEqual({'name': 'Jason'}, actual.body)
