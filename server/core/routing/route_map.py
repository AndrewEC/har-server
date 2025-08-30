from typing import Annotated, List
from functools import lru_cache

from fastapi import Depends
from fastapi.requests import Request

from server.core.har import with_har_parser, HarParser, HarEntry, HarEntryResponse
from server.core.rules.rewrite.request import RequestRewriter, with_request_rewriter
from server.core.rules.rewrite.response import ResponseRewriter, with_response_rewriter
from server.core.rules.matching import with_request_matcher, RequestMatcher

from .request_mapper import RequestMapper, with_request_mapper
from .pre_processor import PreProcessor, with_pre_processor


class RouteMap:

    def __init__(self,
                 har_parser: HarParser,
                 request_rewriter: RequestRewriter,
                 request_matcher: RequestMatcher,
                 request_mapper: RequestMapper,
                 response_rewriter: ResponseRewriter,
                 pre_processor: PreProcessor):

        self._request_rewriter = request_rewriter
        self._request_matcher = request_matcher
        self._request_mapper = request_mapper
        self._response_rewriter = response_rewriter

        self._entries: List[HarEntry] = pre_processor.process_entries(har_parser.get_har_file_contents())

    async def find_entry_for_request(self, request: Request) -> HarEntryResponse | None:
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
            if self._request_matcher.do_requests_match(entry.request, rewritten_incoming_request):
                return self._response_rewriter.apply_response_rewrite_rules(entry.response)
        return None


@lru_cache()
def with_route_map(har_parser: Annotated[HarParser, Depends(with_har_parser)],
                   request_rewriter: Annotated[RequestRewriter, Depends(with_request_rewriter)],
                   request_matcher: Annotated[RequestMatcher, Depends(with_request_matcher)],
                   request_mapper: Annotated[RequestMapper, Depends(with_request_mapper)],
                   response_rewriter: Annotated[ResponseRewriter, Depends(with_response_rewriter)],
                   preprocessor: Annotated[PreProcessor, Depends(with_pre_processor)]) -> RouteMap:

    return RouteMap(
        har_parser,
        request_rewriter,
        request_matcher,
        request_mapper,
        response_rewriter,
        preprocessor
    )
