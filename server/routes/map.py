from typing import List
from itertools import chain
import logging

from fastapi.requests import Request

from server.parse import HarFileContent, HarEntryRequest, HarEntry
from server.rewrite import apply_browser_request_rewrite_rules, apply_entry_request_rewrite_rules
from server.config import Config

from .match import do_requests_match


_log = logging.getLogger(__file__)


class RouteMap:

    def __init__(self):
        self._entries: List[HarEntry] = []

    def set_entries(self, contents: List[HarFileContent]):
        self._entries = list(chain(*[content.entries for content in contents]))

    def _as_har_request(self, request: Request) -> HarEntryRequest:
        query_params = [{'name': key, 'value': str(request.query_params.get(key))} for key in request.query_params.keys()]
        headers = [{'name': key, 'value': str(request.headers.get(key))} for key in request.headers.keys()]
        request_options = {
            'queryString': query_params,
            'method': request.method,
            'url': str(request.url),
            'headers': headers
        }
        return HarEntryRequest(request_options)

    def find_entry_for_request(self, config: Config, request: Request) -> HarEntry | None:
        har_request = apply_browser_request_rewrite_rules(config, self._as_har_request(request))
        for entry in self._entries:
            modified_request_entry = apply_entry_request_rewrite_rules(config, entry.request)
            if do_requests_match(config, modified_request_entry, har_request):
                return entry
        return None
