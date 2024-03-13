from server.parse import HarEntryRequest
from server.config import Config


def do_methods_match(config: Config, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return entry.method == incoming_request.method
