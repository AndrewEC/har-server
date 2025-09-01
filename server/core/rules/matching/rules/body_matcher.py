import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest
from .base import MatcherRule


_log = logging.getLogger(__file__)


class BodyMatcherRule(MatcherRule):

    _APPLICATION_JSON_CONTENT_TYPE = 'application/json'
    _FORM_URL_ENCODED_CONTENT_TYPE = 'application/x-www-form-urlencoded'

    def get_name(self) -> str:
        return 'body'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry body: [{entry.post_data}] to incoming body: [{incoming_request.post_data}]')
        if entry.post_data.mime_type == '' and incoming_request.post_data.mime_type == '':
            return True

        if entry.post_data.mime_type != incoming_request.post_data.mime_type:
            return False

        if BodyMatcherRule._FORM_URL_ENCODED_CONTENT_TYPE in entry.post_data.mime_type:
            return self._match_form_url_encoded_params(entry, incoming_request)
        elif BodyMatcherRule._APPLICATION_JSON_CONTENT_TYPE in entry.post_data.mime_type:
            return entry.post_data.parsed_json == incoming_request.post_data.parsed_json

        return True

    def _match_form_url_encoded_params(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        entry_params = entry.post_data.params
        incoming_params = incoming_request.post_data.params
        if len(entry_params) != len(incoming_params):
            return False

        entry_params = entry_params[:]
        entry_params.sort(key=lambda param: param.name)

        incoming_params = incoming_params[:]
        incoming_params.sort(key=lambda param: param.name)

        for i in range(len(entry_params)):
            first = entry_params[i]
            second = incoming_params[i]
            if first.name != second.name or first.value != second.value:
                return False

        return True
