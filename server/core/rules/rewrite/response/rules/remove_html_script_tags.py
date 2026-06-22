from typing import List
import logging

from bs4 import BeautifulSoup

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader

from .base import ResponseRewriteRule


_log = logging.getLogger(__file__)


class RemoveHtmlScriptTagsResponseRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._removable: List[str] = []

    def get_name(self) -> str:
        return 'remove-html-script-tags'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        if 'text/html' not in response.content.mime_type:
            return response

        try:
            parsed = BeautifulSoup(response.content.text, 'html.parser')
            for script in parsed.find_all('script'):
                script.decompose()
            response.content.text = str(parsed)
        except Exception as e:
            _log.error(f'remove-html-script-tags: Could not remove script tags because the HTML content could not be parsed: [{e}]')

        return response
