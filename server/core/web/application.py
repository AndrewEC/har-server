from typing import Annotated
import logging

from fastapi import FastAPI, Request, Depends, HTTPException, Response

from server.core.config import with_config_loader, with_config_parser
from server.core.config.models import Debug
from server.core.routing import RouteMap, with_route_map

from .transformer import with_response_transformer, ResponseTransformer
from .lifespan import lifespan


app = FastAPI(lifespan=lifespan)
_log = logging.getLogger(__file__)


@app.get('/{full_path:path}')
@app.head('/{full_path:path}')
@app.post('/{full_path:path}')
@app.put('/{full_path:path}')
@app.delete('/{full_path:path}')
@app.options('/{full_path:path}')
@app.patch('/{full_path:path}')
def get(request: Request,
        full_path: str,
        route_map: Annotated[RouteMap, Depends(with_route_map)],
        response_transformer: Annotated[ResponseTransformer, Depends(with_response_transformer)]):

    entry = route_map.find_entry_for_request(request)
    if entry is None:
        raise HTTPException(status_code=404, detail='No har entry matching request found.')

    _log.debug(f'Request [{request.method} {request.url}] matched to [{entry.request.method} {entry.request.url}] '
               f'in .har file [{entry.parent.source_file}]')

    return response_transformer.map_to_fastapi_response(entry.response)


@app.exception_handler(Exception)
def handle_exception(request: Request, exception: Exception):
    _log.error(f'Handling uncaught exception: [{exception}]')
    if with_config_loader(with_config_parser()).read_config(Debug).log_stack_traces:
        _log.exception(exception)
    return Response(status_code=500)
