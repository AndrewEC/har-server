from typing import Annotated, List
from functools import lru_cache
from itertools import chain, filterfalse
import logging

from fastapi import Depends
from fastapi.requests import Request

from server.core.config import ConfigLoader, with_config_loader
from server.core.har import with_har_parser, HarParser, HarFileContent, HarEntry, HarEntryRequest
from server.core.rules.rewrite.request import RequestRewriter, with_request_rewriter
from server.core.rules.matching import with_request_matcher, RequestMatcher
from server.core.rules.exclusions import ExclusionFilter, with_exclusion_filter

from .request_mapper import RequestMapper, with_request_mapper


_log = logging.getLogger(__file__)


class RouteMap:

    def __init__(self,
                 har_parser: HarParser,
                 request_rewriter: RequestRewriter,
                 request_matcher: RequestMatcher,
                 exclusion_filter: ExclusionFilter,
                 request_mapper: RequestMapper,
                 config_loader: ConfigLoader):

        self._request_rewriter = request_rewriter
        self._request_matcher = request_matcher
        self._exclusion_filter = exclusion_filter
        self._request_mapper = request_mapper

        app_config = config_loader.get_app_config()

        self._pre_apply_exclusion_rules = app_config.exclusions.config.pre_apply
        self._exclude_duplicates = app_config.exclusions.config.exclude_duplicate_requests
        self._pre_apply_rewrite_rules = app_config.rewrite.request.config.pre_apply

        self._entries: List[HarEntry] = self._flatten_entries(har_parser.get_har_file_contents())

    def _flatten_entries(self, contents: List[HarFileContent]) -> List[HarEntry]:
        entries = list(chain(*[content.entries for content in contents]))
        _log.info(f'[{len(entries)}] entries were parsed from the har files.')

        if self._pre_apply_exclusion_rules:
            _log.info('Pre-applying entry exclusion rules.')
            # filterfalse because we only want the list of entries to contain
            # entries that are NOT excluded through the configured exclusion rules.
            entries = list(filterfalse(self._exclusion_filter.should_exclude_entry, entries))

        if self._pre_apply_rewrite_rules:
            _log.info('Pre-rewriting entry requests.')
            for entry in entries:
                entry.request = self._request_rewriter.apply_entry_request_rewrite_rules(entry.request)

        if self._exclude_duplicates:
            entries = self._remove_duplicate_entries(entries)

        _log.info(f'[{len(entries)}] har entries are available.')

        return entries

    def _remove_duplicate_entries(self, entries: List[HarEntry]) -> List[HarEntry]:
        _log.info('Excluding duplicate entries by request.')

        indexes_to_exclude: List[int] = []
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                if self._request_matcher.do_requests_match(entries[i].request, entries[j].request):
                    indexes_to_exclude.append(i)
                    break

        return [value for i, value in enumerate(entries) if i not in indexes_to_exclude]

    async def find_entry_for_request(self, request: Request) -> HarEntry | None:
        """
        Attempts to find an entry in a har file in which the request associated with said entry matches the request
        being provided as an input parameter.

        This will immediately return an entry upon a match so no single request will result in more than one match.

        If no match can be found then this will return None.

        :param request: The incoming Http request to match against the requests from each har entry.
        :return: The har entry whose recorded request matches the incoming Http request based on the matching rules.
            If no request matches then this will return None.
        """
        incoming_request = await self._request_mapper.map_to_har_request(request)
        rewritten_incoming_request = self._request_rewriter.apply_browser_request_rewrite_rules(incoming_request)
        for entry in self._entries:
            if self._should_exclude_entry(entry):
                continue
            modified_request_entry = self._get_final_request(entry)
            if self._request_matcher.do_requests_match(modified_request_entry, rewritten_incoming_request):
                return entry
        return None

    def _should_exclude_entry(self, entry: HarEntry) -> bool:
        return not self._pre_apply_exclusion_rules and self._exclusion_filter.should_exclude_entry(entry)

    def _get_final_request(self, entry: HarEntry) -> HarEntryRequest:
        if self._pre_apply_rewrite_rules:
            return entry.request
        return self._request_rewriter.apply_entry_request_rewrite_rules(entry.request)


@lru_cache()
def with_route_map(har_parser: Annotated[HarParser, Depends(with_har_parser)],
                   request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                   request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)],
                   exclusion_filter: Annotated[ExclusionFilter, Depends(with_exclusion_filter)],
                   request_mapper: Annotated[RequestMapper, Depends(with_request_mapper)],
                   config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RouteMap:

    return RouteMap(har_parser, request_rewriter, request_matcher, exclusion_filter, request_mapper, config_loader)
