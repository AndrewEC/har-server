import logging

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader
from server.core.config.models import ResponseRuleConfig

from .base import ResponseRewriteRule


_log = logging.getLogger(__file__)


class RemoveCookiesResponseRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._removable = []

    def load_config(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(ResponseRuleConfig).removable_cookies
        if len(self._removable) == 0:
            raise Exception('The remove-cookies response rewrite rule is enabled but no '
                            'removable-cookies have been configured configured.')

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        for cookie in self._removable:
            if cookie not in response.cookies:
                continue
            response.cookies.pop(cookie)
        return response
