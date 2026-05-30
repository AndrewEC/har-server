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
        _log.info(f"A total of [{len(entries)}] har entries were loaded.")

        entries = self._apply_exclusion_rules(entries)
        self._apply_rewrite_rules(entries)

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


@lru_cache()
def with_pre_processor(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)],
                       exclusion_filter: Annotated[ExclusionFilter, Depends(with_exclusion_filter)],
                       request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                       request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)]) -> PreProcessor:

    return PreProcessor(config_loader, exclusion_filter, request_rewriter, request_matcher)
