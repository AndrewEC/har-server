from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest


def do_paths_match(config: ConfigLoader, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return entry_request.path == incoming_request.path
