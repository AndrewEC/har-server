from typing import Annotated, List
from functools import lru_cache
from itertools import chain

from fastapi import Depends
from fastapi.requests import Request

from server.core.har import with_har_parser, HarParser, HarFileContent, HarEntry
from server.core.rules.rewrite.request import RequestRewriter, with_request_rewriter
from server.core.rules.matching import with_request_matcher, RequestMatcher
from server.core.rules.exclusions import ExclusionFilter, with_exclusion_filter

from .request_mapper import RequestMapper, with_request_mapper


class RouteMap:

    def __init__(self,
                 har_parser: HarParser,
                 request_rewriter: RequestRewriter,
                 request_matcher: RequestMatcher,
                 exclusion_filter: ExclusionFilter,
                 request_mapper: RequestMapper):

        self._entries: List[HarEntry] = self._flatten_entries(har_parser.get_har_file_contents())
        self._request_rewriter = request_rewriter
        self._request_matcher = request_matcher
        self._exclusion_filter = exclusion_filter
        self._request_mapper = request_mapper

    def _flatten_entries(self, contents: List[HarFileContent]) -> List[HarEntry]:
        return list(chain(*[content.entries for content in contents]))

    def find_entry_for_request(self, request: Request) -> HarEntry | None:
        """
        Attempts to find an entry in a har file in which the request associated with said entry matches the request
        being provided as an input parameter.

        This will immediately return an entry upon a match so no single request will result in more than one match.

        If no match can be found then this will return None.

        :param request: The incoming Http request to match against the requests from each har entry.
        :return: The har entry whose recorded request matches the incoming Http request based on the matching rules.
            If no request matches then this will return None.
        """
        incoming_request = self._request_mapper.map_to_har_request(request)
        rewritten_incoming_request = self._request_rewriter.apply_browser_request_rewrite_rules(incoming_request)
        for entry in self._entries:
            if self._exclusion_filter.should_exclude_entry(entry):
                continue
            modified_request_entry = self._request_rewriter.apply_entry_request_rewrite_rules(entry.request)
            if self._request_matcher.do_requests_match(modified_request_entry, rewritten_incoming_request):
                return entry
        return None


@lru_cache()
def with_route_map(har_parser: Annotated[HarParser, Depends(with_har_parser)],
                   request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                   request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)],
                   exclusion_filter: Annotated[ExclusionFilter, Depends(with_exclusion_filter)],
                   request_mapper: Annotated[RequestMapper, Depends(with_request_mapper)]) -> RouteMap:

    return RouteMap(har_parser, request_rewriter, request_matcher, exclusion_filter, request_mapper)
