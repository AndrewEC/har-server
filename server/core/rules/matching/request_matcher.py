from typing import Annotated, Final, Dict, Callable
from functools import lru_cache
import copy
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.har import HarEntryRequest, HarEntry
from server.core.rules.base.error import RuleNotFoundException


_log = logging.getLogger(__file__)


class RequestMatcher:

    _HASH_FUNCTIONS: Final[Dict[str, Callable[[HarEntryRequest], str]]] = {
        'method': lambda request: request.method,
        'path': lambda request: request.path if request.path is not None else '',
        'query-params': lambda request: request.hashes.query_params,
        'headers': lambda request: request.hashes.headers,
        'cookies': lambda request: request.hashes.cookies,
        'body': lambda request: request.hashes.post_data
    }

    def __init__(self, config_loader: ConfigLoader):
        self._enabled_rules = config_loader.get_app_config().request_matching.rules
        _log.info(f'Configured request matching rules: [{self._enabled_rules}]')

        all_rules = list(self._HASH_FUNCTIONS.keys())
        for enabled_rule in self._enabled_rules:
            if enabled_rule not in all_rules:
                raise RuleNotFoundException('request-matcher', enabled_rule)

        self._available_entries: Dict[str, HarEntry] = dict()

    def accumulate(self, entry: HarEntry) -> bool:
        key = self._get_complete_hash(entry.request)
        if key not in self._available_entries:
            self._available_entries[key] = entry
            return True
        return False

    def find_matching_entry(self, request: HarEntryRequest) -> HarEntry | None:
        matching = self._available_entries.get(self._get_complete_hash(request))
        if matching is not None:
            return copy.deepcopy(matching)
        return None
    
    def _get_complete_hash(self, request: HarEntryRequest) -> str:
        entry_hash = ''
        for key in RequestMatcher._HASH_FUNCTIONS.keys():
            if key in self._enabled_rules:
                entry_hash = entry_hash + '-' + RequestMatcher._HASH_FUNCTIONS[key](request)
        return entry_hash


@lru_cache()
def with_request_matcher(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestMatcher:
    return RequestMatcher(config_loader)
