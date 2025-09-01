import unittest
from unittest.mock import AsyncMock

from server.core.routing import RequestMapper


class RequestMapperTest(unittest.IsolatedAsyncioTestCase):

    async def test_map_to_har_request_with_json_body(self):
        request = AsyncMock(
            query_params={'query_param_name': 'query_param_value'},
            headers={'header_name': 'header_value', 'content-type': 'application/json'},
            cookies={'cookie_name': 'cookie_value'},
            url='http://www.test.com',
            method='post',
            body=AsyncMock(return_value=b'{"name":"Jason"}')
        )

        actual = await RequestMapper().map_to_har_request(request)

        self.assertEqual(2, len(actual.headers))
        self.assertEqual('header_name', actual.headers[0].name)
        self.assertEqual('header_value', actual.headers[0].value)
        self.assertEqual('content-type', actual.headers[1].name)
        self.assertEqual('application/json', actual.headers[1].value)

        self.assertEqual(1, len(actual.query_params))
        self.assertEqual('query_param_name', actual.query_params[0].name)
        self.assertEqual('query_param_value', actual.query_params[0].value)

        self.assertEqual(1, len(actual.cookies))
        self.assertEqual('cookie_name', actual.cookies[0].name)
        self.assertEqual('cookie_value', actual.cookies[0].value)

        self.assertEqual(request.url, actual.url)
        self.assertEqual(request.method, actual.method)

        self.assertEqual({'name': 'Jason'}, actual.post_data.parsed_json)
        self.assertEqual('application/json', actual.post_data.mime_type)

    async def test_map_to_har_request_with_form_url_encoded_body(self):
        request = AsyncMock(
            query_params={'query_param_name': 'query_param_value'},
            headers={'header_name': 'header_value', 'content-type': 'application/x-www-form-urlencoded'},
            cookies={'cookie_name': 'cookie_value'},
            url='http://www.test.com',
            method='post',
            body=AsyncMock(return_value=b'name=Jason')
        )

        actual = await RequestMapper().map_to_har_request(request)

        self.assertEqual(2, len(actual.headers))
        self.assertEqual('header_name', actual.headers[0].name)
        self.assertEqual('header_value', actual.headers[0].value)
        self.assertEqual('content-type', actual.headers[1].name)
        self.assertEqual('application/x-www-form-urlencoded', actual.headers[1].value)

        self.assertEqual(1, len(actual.query_params))
        self.assertEqual('query_param_name', actual.query_params[0].name)
        self.assertEqual('query_param_value', actual.query_params[0].value)

        self.assertEqual(1, len(actual.cookies))
        self.assertEqual('cookie_name', actual.cookies[0].name)
        self.assertEqual('cookie_value', actual.cookies[0].value)

        self.assertEqual(request.url, actual.url)
        self.assertEqual(request.method, actual.method)

        self.assertEqual(1, len(actual.post_data.params))
        self.assertEqual('name', actual.post_data.params[0].name)
        self.assertEqual('Jason', actual.post_data.params[0].value)
        self.assertEqual('application/x-www-form-urlencoded', actual.post_data.mime_type)
