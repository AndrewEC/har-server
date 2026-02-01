from __future__ import annotations
from typing import List
import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryResponse

from .base import ResponseRewriteRule
from .url_origin_captor import UrlOriginCaptor, CapturedOrigin


_log = logging.getLogger(__file__)


_LOCALHOST = 'http://localhost:8080'


class RewriteUrlResponseRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._excluded_domains: List[str] = []

    def get_name(self) -> str:
        return 'urls-in-response'

    def initialize(self, config_loader: ConfigLoader):
        self._excluded_domains = config_loader.get_app_config().rewrite.response.config.excluded_domains

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        content = response.content.text
        if len(content) == 0:
            return response

        capture_results = UrlOriginCaptor(content).capture_origin_locations().get_capture_results()
        if len(capture_results) == 0:
            return response

        response.content.text = self._replace_all_captured_origins(content, capture_results, self._excluded_domains)
        return response

    def _replace_all_captured_origins(self,
                                      content: str,
                                      capture_results: List[CapturedOrigin],
                                      excluded_domains: List[str]) -> str:

        # The modifier is used to capture the change in the length of the input content string as each
        # captured domain is replaced with the localhost domain.
        modifier = 0
        for captured in capture_results:
            new_content = self._replace_captured_origin(content, captured, modifier, excluded_domains)
            modifier = modifier + (len(content) - len(new_content))
            content = new_content
        return content

    def _replace_captured_origin(self,
                                 content: str,
                                 captured: CapturedOrigin,
                                 modifier: int,
                                 excluded_domains: List[str]) -> str:

        start_index = captured.start_index - modifier
        origin = content[start_index:start_index + captured.length]
        if origin in excluded_domains:
            _log.debug(f'Skipping excluded domain: [{origin}]')
            return content
        _log.debug(f'Replacing with localhost: [{origin}]')
        return content[:start_index] + _LOCALHOST + content[start_index + captured.length:]
