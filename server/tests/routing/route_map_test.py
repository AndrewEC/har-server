import unittest
from unittest.mock import Mock, patch

from server.core.config import ConfigLoader
from server.core.config.models import RequestRewriteConfig, ExclusionConfig
from server.core.rules.matching import RequestMatcher
from server.core.rules.rewrite.request import RequestRewriter
from server.core.routing.request_mapper import RequestMapper
from server.core.har import HarParser
from server.core.routing import RouteMap
from server.core.rules.exclusions import ExclusionFilter

from server.tests.util import fully_qualified_name


class RouteMapTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    @patch(fully_qualified_name(RequestMatcher))
    @patch(fully_qualified_name(ExclusionFilter))
    @patch(fully_qualified_name(RequestRewriter))
    @patch(fully_qualified_name(RequestMapper))
    @patch(fully_qualified_name(HarParser))
    def test_find_entry_for_request(self,
                                    mock_har_parser: HarParser,
                                    mock_request_mapper: RequestMapper,
                                    mock_request_rewriter: RequestRewriter,
                                    mock_exclusion_filter: ExclusionFilter,
                                    mock_request_matcher: RequestMatcher,
                                    mock_config_loader: ConfigLoader):

        mock_config_loader.read_config = Mock(side_effect=[ExclusionConfig(), RequestRewriteConfig()])

        incoming_request = Mock()
        mock_request_mapper.map_to_har_request = Mock(return_value=incoming_request)

        rewritten_incoming_request = Mock()
        rewritten_entry_request = Mock()
        mock_request_rewriter.apply_browser_request_rewrite_rules = Mock(return_value=rewritten_incoming_request)
        mock_request_rewriter.apply_entry_request_rewrite_rules = Mock(return_value=rewritten_entry_request)

        mock_exclusion_filter.should_exclude_entry = Mock(return_value=False)

        har_entry = Mock(request=Mock())
        mock_har_parser.get_har_file_contents = Mock(return_value=[Mock(entries=[har_entry])])

        mock_request_matcher.do_requests_match = Mock(return_value=True)

        sut = RouteMap(mock_har_parser, mock_request_rewriter, mock_request_matcher, mock_exclusion_filter,
                       mock_request_mapper, mock_config_loader)

        request = Mock()
        actual = sut.find_entry_for_request(request)

        self.assertIsNotNone(actual)

        mock_har_parser.get_har_file_contents.assert_called_once()
        mock_request_mapper.map_to_har_request.assert_called_once_with(request)
        mock_request_rewriter.apply_browser_request_rewrite_rules.assert_called_once_with(incoming_request)
        mock_request_rewriter.apply_entry_request_rewrite_rules.assert_called_once_with(har_entry.request)
        mock_exclusion_filter.should_exclude_entry.assert_called_once_with(har_entry)
        mock_request_matcher.do_requests_match.assert_called_once_with(rewritten_entry_request, rewritten_incoming_request)

