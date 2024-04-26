from server.har import HarEntryRequest
from server.config import ConfigLoader


def do_methods_match(config: ConfigLoader, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return entry.method == incoming_request.method
