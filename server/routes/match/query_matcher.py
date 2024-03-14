from server.config import Config
from server.parse import HarEntryRequest


def do_queries_match(config: Config, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    entry_params = entry_request.query_params
    incoming_params = incoming_request.query_params
    if len(entry_params) != len(incoming_params):
        return False

    for entry_param in entry_params.keys():
        if entry_param not in incoming_params or entry_params[entry_param] != incoming_params[entry_param]:
            return False
    return True
