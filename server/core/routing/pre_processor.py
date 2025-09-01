from typing import Annotated, List
from functools import lru_cache
from itertools import chain, filterfalse
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.har.models import HarFileContent, HarEntry
from server.core.rules.exclusions import ExclusionFilter, with_exclusion_filter
from server.core.rules.rewrite.request import RequestRewriter, with_request_rewriter
from server.core.rules.matching import RequestMatcher, with_request_matcher


_log = logging.getLogger(__file__)


class PreProcessor:

    def __init__(self, config_loader: ConfigLoader,
                 exclusion_filter: ExclusionFilter,
                 request_rewriter: RequestRewriter,
                 request_matcher: RequestMatcher):

        app_config = config_loader.get_app_config()

        self._exclusion_filter = exclusion_filter
        self._request_rewriter = request_rewriter
        self._request_matcher = request_matcher

        self._exclude_duplicates = app_config.exclusions.config.exclude_duplicate_requests

    def process_entries(self, har_file_contents: List[HarFileContent]) -> List[HarEntry]:
        entries = list(chain(*[content.log.entries for content in har_file_contents]))
        _log.info(f"[{len(entries)}] entries will be processed.")

        entries = self._apply_exclusion_rules(entries)
        self._apply_rewrite_rules(entries)
        entries = self._remove_duplicate_entries(entries)

        _log.info(f'[{len(entries)}] har entries remain available.')

        return entries

    def _apply_exclusion_rules(self, entries: List[HarEntry]) -> List[HarEntry]:
        _log.info('Pre-applying entry exclusion rules.')
        # filterfalse because we only want the list of entries to contain
        # entries that are NOT excluded through the configured exclusion rules.
        result = list(filterfalse(self._exclusion_filter.should_exclude_entry, entries))

        _log.info(f'[{len(result)}] entries remain after applying exclusion rules.')

        return result

    def _apply_rewrite_rules(self, entries: List[HarEntry]):
        _log.info('Pre-rewriting entry requests.')
        for entry in entries:
            entry.request = self._request_rewriter.apply_entry_request_rewrite_rules(entry.request)

    def _remove_duplicate_entries(self, entries: List[HarEntry]) -> List[HarEntry]:
        if not self._exclude_duplicates:
            return entries

        _log.info('Excluding duplicate entries by request.')

        indexes_to_exclude: List[int] = []
        for i in range(len(entries) - 1, -1, -1):
            for j in range(i - 1, -1, -1):
                if self._request_matcher.do_requests_match(entries[i].request, entries[j].request):
                    indexes_to_exclude.append(i)
                    break

        return [value for i, value in enumerate(entries) if i not in indexes_to_exclude]


@lru_cache
def with_pre_processor(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)],
                       exclusion_filter: Annotated[ExclusionFilter, Depends(with_exclusion_filter)],
                       request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                       request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)]) -> PreProcessor:

    return PreProcessor(config_loader, exclusion_filter, request_rewriter, request_matcher)
