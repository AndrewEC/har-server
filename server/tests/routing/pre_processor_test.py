import unittest
from unittest.mock import patch, Mock, call, MagicMock

from server.core.rules.exclusions import ExclusionFilter
from server.core.rules.rewrite.request import RequestRewriter
from server.core.rules.matching import RequestMatcher
from server.core.routing import PreProcessor
from server.core.rules.rewrite.response.response_rewriter import ResponseRewriter

from ..util import fully_qualified_name


class PreProcessTest(unittest.TestCase):

    @patch(fully_qualified_name(ResponseRewriter))
    @patch(fully_qualified_name(RequestMatcher))
    @patch(fully_qualified_name(RequestRewriter))
    @patch(fully_qualified_name(ExclusionFilter))
    def test_process_entries(self,
                             mock_exclusion_filter: ExclusionFilter,
                             mock_request_rewriter: RequestRewriter,
                             mock_request_matcher: RequestMatcher,
                             mock_response_rewriter: ResponseRewriter):
        
        # Stub values.
        to_rewrite_request = Mock()
        to_rewrite_request_2 = Mock()
        to_rewrite_response = Mock()

        entries = [
            MagicMock(
                request = Mock(),
                response = Mock()
            ),
            MagicMock(
                request = to_rewrite_request,
                response = Mock()
            ),
            MagicMock(
                request = to_rewrite_request_2,
                response = to_rewrite_response
            )
        ]
        har_content = MagicMock(log = MagicMock(entries = entries))

        modified_request = Mock()
        modified_response = Mock()

        # Mock return values.
        mock_exclusion_filter.should_exclude_entry = Mock(side_effect=[True, False, False])
        mock_request_rewriter.apply_entry_request_rewrite_rules = Mock(return_value=modified_request)
        mock_response_rewriter.apply_response_rewrite_rules = Mock(return_value=modified_response)
        mock_request_matcher.accumulate = Mock(side_effect=[False, True])

        # Execute.
        sut = PreProcessor(
            mock_exclusion_filter,
            mock_request_rewriter,
            mock_request_matcher,
            mock_response_rewriter
        )

        sut.process_content(har_content)

        # Assert expectations.
        mock_exclusion_filter.should_exclude_entry.assert_has_calls(
            [
                call(entries[0]),
                call(entries[1]),
                call(entries[2])
            ]
        )

        mock_request_rewriter.apply_entry_request_rewrite_rules.assert_has_calls(
            [
                call(to_rewrite_request),
                call(to_rewrite_request_2)
            ]
        )

        mock_response_rewriter.apply_response_rewrite_rules.assert_called_once_with(to_rewrite_response)
