from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .common import do_dicts_contain_same_elements


def do_headers_match(config: ConfigLoader, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return do_dicts_contain_same_elements(entry_request.headers, incoming_request.headers)
