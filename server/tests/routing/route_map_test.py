import unittest
from unittest.mock import Mock, patch, AsyncMock

from server.core.rules.matching import RequestMatcher
from server.core.rules.rewrite.request import RequestRewriter
from server.core.rules.rewrite.response import ResponseRewriter
from server.core.routing.request_mapper import RequestMapper
from server.core.har import HarParser
from server.core.routing import RouteMap, PreProcessor

from server.tests.util import fully_qualified_name


class RouteMapTest(unittest.IsolatedAsyncioTestCase):

    @patch(fully_qualified_name(PreProcessor))
    @patch(fully_qualified_name(ResponseRewriter))
    @patch(fully_qualified_name(RequestMapper))
    @patch(fully_qualified_name(RequestMatcher))
    @patch(fully_qualified_name(RequestRewriter))
    @patch(fully_qualified_name(HarParser))
    async def test_find_entry_for_request(self,
                                          mock_har_parser: HarParser,
                                          mock_request_rewriter: RequestRewriter,
                                          mock_request_matcher: RequestMatcher,
                                          mock_request_mapper: RequestMapper,
                                          mock_response_rewriter: ResponseRewriter,
                                          mock_pre_processor: PreProcessor):
            
            har_entry_request = Mock()
            har_entry = Mock(request=har_entry_request)
            entries = [har_entry]
            mock_har_parser.get_har_file_contents = Mock(return_value=entries)
            mock_pre_processor.process_entries = Mock(return_value=entries)

            incoming_request = Mock()
            mock_request_mapper.map_to_har_request = AsyncMock(return_value=incoming_request)

            rewritten_incoming_request = Mock()
            mock_request_rewriter.apply_browser_request_rewrite_rules = Mock(return_value=rewritten_incoming_request)

            mock_request_matcher.do_requests_match = Mock(return_value=True)

            sut = RouteMap(
                mock_har_parser,
                mock_request_rewriter,
                mock_request_matcher,
                mock_request_mapper,
                mock_response_rewriter,
                mock_pre_processor
            )

            request = Mock()
            actual = await sut.find_entry_for_request(request)

            self.assertIsNotNone(actual)

            mock_har_parser.get_har_file_contents.assert_called_once()
            mock_request_mapper.map_to_har_request.assert_called_once_with(request)
            mock_request_rewriter.apply_browser_request_rewrite_rules.assert_called_once_with(incoming_request)
            mock_request_matcher.do_requests_match.assert_called_once_with(har_entry.request, rewritten_incoming_request)
            mock_pre_processor.process_entries.assert_called_once_with(entries)
