from typing import Annotated
import logging

from fastapi import FastAPI, Request, Depends, HTTPException, Response

from server.config import with_config_loader
from server.config.models import Debug
from server.debug import enable_debug_logs
from server.har import with_har_parser
from server.routing import RouteMap, with_route_map

from .transformer import with_response_transformer, ResponseTransformer
from .browser_open import open_browser_in_background


app = FastAPI()
_log = logging.getLogger(__file__)


@app.get('/{full_path:path}')
@app.post('/{full_path:path}')
def get(request: Request,
        full_path: str,
        route_map: Annotated[RouteMap, Depends(with_route_map)],
        response_transformer: Annotated[ResponseTransformer, Depends(with_response_transformer)]):

    entry = route_map.find_entry_for_request(request)
    if entry is None:
        raise HTTPException(status_code=404, detail='No har entry matching request found.')

    _log.debug(f'Request [{request.method} {request.url}] matched to [{entry.request.method} {entry.request.url}] '
               f'in .har file [{entry.parent.source_file}]')

    return response_transformer.map_har_response_to_fastapi_response(entry.response)


@app.exception_handler(Exception)
def handle_exception(request: Request, exception: Exception):
    _log.error(f'Handling uncaught exception: [{exception}]')
    if with_config_loader().read_config(Debug).log_stack_traces:
        _log.exception(exception)
    return Response(status_code=500)


@app.on_event('startup')
def startup():
    config_loader = with_config_loader()

    debug_config = config_loader.read_config(Debug)
    if debug_config.enable_debug_logs:
        enable_debug_logs()

    with_har_parser().get_har_file_contents()

    open_browser_in_background(config_loader)
