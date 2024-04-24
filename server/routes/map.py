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
        """
        Sets the list of entries containing the requests to be matched against and the responses to be returned when
        a request is matched.

        This will take all the entries from all the parsed har files and put them in a single unsorted list.

        :param contents: The list of parsed har files containing the entries to be referenced.
        """
        self._entries = list(chain(*[content.entries for content in contents]))

    def _as_har_request(self, request: Request) -> HarEntryRequest:
        query_params = [{'name': key, 'value': request.query_params.get(key)} for key in request.query_params.keys()]
        headers = [{'name': key, 'value': request.headers.get(key)} for key in request.headers.keys()]
        cookies = [{'name': key, 'value': request.cookies.get(key)} for key in request.cookies.keys()]
        request_options = {
            'queryString': query_params,
            'method': request.method,
            'url': str(request.url),
            'headers': headers,
            'cookies': cookies
        }
        return HarEntryRequest(request_options)

    def find_entry_for_request(self, config: Config, request: Request) -> HarEntry | None:
        """
        Attempts to find an entry in a har file in which the request associated with said entry matches the request
        being provided as an input parameter.

        This will immediately return an entry upon a match so no single request will result in more than one match.

        If no match can be found then this will return None.

        :param config: The har-server configuration from which the list of match rules will be pulled.
        :param request: The incoming Http request to match against the requests from each har entry.
        :return: The har entry whose recorded request matches the incoming Http request based on the matching rules.
            If no request matches then this will return None.
        """
        har_request = apply_browser_request_rewrite_rules(config, self._as_har_request(request))
        for entry in self._entries:
            modified_request_entry = apply_entry_request_rewrite_rules(config, entry.request)
            if do_requests_match(config, modified_request_entry, har_request):
                return entry
        return None
