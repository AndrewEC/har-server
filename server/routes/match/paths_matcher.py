from server.config import Config
from server.parse import HarEntryRequest


def do_paths_match(config: Config, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    return entry_request.path == incoming_request.path
