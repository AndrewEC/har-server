from server.config import Config
from server.parse import HarEntryRequest


def do_headers_match(config: Config, entry_request: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
    entry_headers = entry_request.headers
    incoming_headers = incoming_request.headers
    if len(entry_headers) != len(incoming_headers):
        return False

    for entry_header in entry_headers.keys():
        if entry_header not in incoming_headers or entry_headers[entry_header] != incoming_headers[entry_header]:
            return False

    return True

