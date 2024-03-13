from server.config import Config
from server.parse import HarEntryRequest


def do_queries_match(config: Config, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    if len(entry_request.query_params) != len(incoming_request.query_params):
        return False

    for entry_param in entry_request.query_params.keys():
        if (entry_param not in incoming_request.query_params
                or entry_request.query_params[entry_param] != incoming_request.query_params[entry_param]):
            return False
    return True
