from typing import Annotated
from functools import lru_cache
from itertools import filterfalse
import logging

from fastapi import Depends

from server.core.har.models import HarFileContent
from server.core.rules.exclusions import ExclusionFilter, with_exclusion_filter
from server.core.rules.rewrite.request import RequestRewriter, with_request_rewriter
from server.core.rules.matching import RequestMatcher, with_request_matcher
from server.core.rules.rewrite.response import ResponseRewriter, with_response_rewriter


_log = logging.getLogger(__file__)


class PreProcessor:

    def __init__(self,
                 exclusion_filter: ExclusionFilter,
                 request_rewriter: RequestRewriter,
                 request_matcher: RequestMatcher,
                 response_rewriter: ResponseRewriter):

        self._exclusion_filter = exclusion_filter
        self._request_rewriter = request_rewriter
        self._request_matcher = request_matcher
        self._response_rewriter = response_rewriter

    def process_content(self, har_file_contents: HarFileContent):
        entries = har_file_contents.log.entries
        _log.debug(f'Har file contains [{len(entries)}] entries.')

        # filterfalse because we only want the list of entries to contain
        # entries that are NOT excluded through the configured exclusion rules.
        _log.debug('Applying entry exclusion rules...')
        entries = list(filterfalse(self._exclusion_filter.should_exclude_entry, entries))
        _log.debug(f'[{len(entries)}] remain after applying exclusion rules.')

        _log.debug('Accumulating distinct entries...')
        count = 0
        for entry in entries:
            entry.request = self._request_rewriter.apply_entry_request_rewrite_rules(entry.request)
            if self._request_matcher.accumulate(entry):
                count = count + 1
                entry.response = self._response_rewriter.apply_response_rewrite_rules(entry.response)
        _log.debug(f'[{count}] distinct entries remain.')
        


@lru_cache()
def with_pre_processor(exclusion_filter: Annotated[ExclusionFilter, Depends(with_exclusion_filter)],
                       request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                       request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)],
                       response_rewriter: Annotated[ResponseRewriter, Depends(with_response_rewriter)]) -> PreProcessor:

    return PreProcessor(exclusion_filter, request_rewriter, request_matcher, response_rewriter)
