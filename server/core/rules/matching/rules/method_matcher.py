from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader


def do_methods_match(config: ConfigLoader, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return entry.method == incoming_request.method
