import unittest
from unittest.mock import Mock

from server.core.web.response_transformer import ResponseTransformer


class ResponseTransformerTest(unittest.TestCase):

    def test_map_to_fastapi_response(self):
        initial_response = Mock(
            status=200,
            content=Mock(
                text='response_content',
                mime_type='text/plain'
            ),
            headers={'header-name': 'header-value'},
            cookies={'cookie-name': 'cookie-value'}
        )

        actual = ResponseTransformer().map_to_fastapi_response(initial_response)

        self.assertEqual(initial_response.status, actual.status_code)
        self.assertEqual(initial_response.content.mime_type, actual.media_type)
        self.assertEqual(initial_response.content.text, actual.body.decode('utf-8')) # type: ignore

        for header in initial_response.headers:
            self.assertIn(header, actual.headers)
            self.assertEqual(initial_response.headers[header], actual.headers[header])
    
    def test_map_to_fastapi_response_base64_content(self):
        initial_response = Mock(
            status=200,
            content=Mock(
                encoding='base64',
                text='cmVzcG9uc2VfY29udGVudA==',
                mime_type='image/png'
            ),
            headers={'header-name': 'header-value'},
            cookies={'cookie-name': 'cookie-value'}
        )

        actual = ResponseTransformer().map_to_fastapi_response(initial_response)

        self.assertIsNotNone(actual)
        self.assertEqual('response_content', actual.body.decode('utf-8'))  # type: ignore
        self.assertEqual(initial_response.status, actual.status_code)
        self.assertEqual(initial_response.content.mime_type, actual.media_type)
