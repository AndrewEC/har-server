from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .common import do_dicts_contain_same_elements


def do_queries_match(config: ConfigLoader, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return do_dicts_contain_same_elements(entry_request.query_params, incoming_request.query_params)
