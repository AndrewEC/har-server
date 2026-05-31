import unittest
from unittest.mock import patch, Mock, call

from server.core.rules.exclusions import ExclusionFilter
from server.core.rules.rewrite.request import RequestRewriter
from server.core.rules.matching import RequestMatcher
from server.core.routing import PreProcessor

from ..util import fully_qualified_name


class PreProcessTests(unittest.TestCase):

    @patch(fully_qualified_name(RequestMatcher))
    @patch(fully_qualified_name(RequestRewriter))
    @patch(fully_qualified_name(ExclusionFilter))
    def test_process_entries(self,
                             mock_exclusion_filter: ExclusionFilter,
                             mock_request_rewriter: RequestRewriter,
                             mock_request_matcher: RequestMatcher):
        
        # Stub values.
        entries = [
            Mock(
                request = Mock(),
                response = Mock()
            ),
            Mock(
                request = Mock(),
                response = Mock()
            ),
            Mock(
                request = Mock(),
                response = Mock()
            )
        ]
        har_content = Mock(entries = entries)

        modified_request = Mock()

        # Mock return values.
        mock_exclusion_filter.should_exclude_entry = Mock(side_effect=[False, False, True])
        mock_request_rewriter.apply_entry_request_rewrite_rules = Mock(return_value=modified_request)

        # Execute.
        sut = PreProcessor(
            mock_exclusion_filter,
            mock_request_rewriter,
            mock_request_matcher
        )

        actual = sut.process_entries([har_content])

        self.assertEqual(1, len(actual))

        # Assert expectations.
        mock_exclusion_filter.should_exclude_entry.assert_has_calls(
            [call(entries[0]), call(entries[1]), call(entries[2])]
        )
        mock_request_rewriter.apply_entry_request_rewrite_rules.assert_has_calls(
            [call(entries[0].request), call(entries[1].request)]
        )
