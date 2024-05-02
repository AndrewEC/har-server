import unittest
from unittest.mock import Mock, MagicMock, patch

from server.core.web.transformer import ResponseTransformer
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
        mock_response_rewriter.apply_response_rewrite_rules = MagicMock(return_value=rewritten_response)

        actual = ResponseTransformer(mock_response_rewriter).map_to_fastapi_response(initial_response)

        self.assertEqual(rewritten_response.status, actual.status_code)
        self.assertEqual(rewritten_response.content.mime_type, actual.media_type)
        self.assertEqual(rewritten_response.content.text, actual.body.decode('utf-8'))

        for header in rewritten_response.headers:
            self.assertIn(header, actual.headers)
            self.assertEqual(rewritten_response.headers[header], actual.headers[header])

        mock_response_rewriter.apply_response_rewrite_rules.assert_called_once_with(initial_response)
