import logging

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import ResponseRuleConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import ResponseRewriteRule


_log = logging.getLogger(__file__)


class RemoveCookiesResponseRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._removable = []

    def get_name(self) -> str:
        return 'remove-cookies'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(ResponseRuleConfig).removable_cookies
        if len(self._removable) == 0:
            property_path = get_prop_config_path(ResponseRuleConfig, 'removable_cookies')
            raise MissingConfigPropertyException(self.get_name(), property_path)

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        for cookie in self._removable:
            if cookie not in response.cookies:
                continue
            response.cookies.pop(cookie)
        return response
