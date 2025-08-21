import unittest
from unittest.mock import Mock, patch

from server.core.web.response_transformer import ResponseTransformer
from server.core.rules.rewrite.response import ResponseRewriter

from server.tests.util import fully_qualified_name


class ResponseTransformerTest(unittest.TestCase):

    @patch(fully_qualified_name(ResponseRewriter))
    def test_map_to_fastapi_response(self, mock_response_rewriter: ResponseRewriter):
        initial_response = Mock()

        rewritten_response = Mock(
            status=200,
            content=Mock(
                text='response_content',
                mime_type='text/plain'
            ),
            headers={'header-name': 'header-value'},
            cookies={'cookie-name': 'cookie-value'}
        )
        mock_response_rewriter.apply_response_rewrite_rules = Mock(return_value=rewritten_response)

        actual = ResponseTransformer(mock_response_rewriter).map_to_fastapi_response(initial_response)

        self.assertEqual(rewritten_response.status, actual.status_code)
        self.assertEqual(rewritten_response.content.mime_type, actual.media_type)
        self.assertEqual(rewritten_response.content.text, actual.body.decode('utf-8')) # type: ignore

        for header in rewritten_response.headers:
            self.assertIn(header, actual.headers)
            self.assertEqual(rewritten_response.headers[header], actual.headers[header])

        mock_response_rewriter.apply_response_rewrite_rules.assert_called_once_with(initial_response)
    
    @patch(fully_qualified_name(ResponseRewriter))
    def test_map_to_fastapi_response_base64_content(self, mock_response_rewriter: ResponseRewriter):
        mock_response_rewriter.apply_response_rewrite_rules = Mock()

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

        actual = ResponseTransformer(mock_response_rewriter).map_to_fastapi_response(initial_response)

        self.assertIsNotNone(actual)
        self.assertEqual('response_content', actual.body.decode('utf-8'))  # type: ignore
        self.assertEqual(initial_response.status, actual.status_code)
        self.assertEqual(initial_response.content.mime_type, actual.media_type)

        mock_response_rewriter.apply_response_rewrite_rules.assert_not_called()
