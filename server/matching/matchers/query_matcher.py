from server.config import ConfigLoader
from server.har import HarEntryRequest

from .common import are_dictionaries_equal


def do_queries_match(config: ConfigLoader, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return are_dictionaries_equal(entry_request.query_params, incoming_request.query_params)
