from server.har import HarEntryRequest
from server.config import ConfigLoader

from .common import are_dictionaries_equal


def do_cookies_match(config: ConfigLoader, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return are_dictionaries_equal(entry.cookies, incoming_request.cookies)
