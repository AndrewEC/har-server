from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader

from .common import do_dicts_contain_same_elements


def do_cookies_match(config: ConfigLoader, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return do_dicts_contain_same_elements(entry.cookies, incoming_request.cookies)
