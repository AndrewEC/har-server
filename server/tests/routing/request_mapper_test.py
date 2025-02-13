import unittest
from unittest.mock import AsyncMock

from server.core.routing.request_mapper import RequestMapper


class RequestMapperTest(unittest.IsolatedAsyncioTestCase):

    async def test_map_to_har_request(self):
        request = AsyncMock(
            query_params={'query_param_name': 'query_param_value'},
            headers={'header_name': 'header_value'},
            cookies={'cookie_name': 'cookie_value'},
            url='http://www.test.com',
            method='POST',
            body=AsyncMock(return_value=b'{}')
        )

        actual = await RequestMapper().map_to_har_request(request)

        self.assertEqual(request.query_params, actual.query_params)
        self.assertEqual(request.headers, actual.headers)
        self.assertEqual(request.cookies, actual.cookies)
        self.assertEqual(request.url, actual.url)
        self.assertEqual(request.method, actual.method)
        self.assertEqual(dict(), actual.body)
