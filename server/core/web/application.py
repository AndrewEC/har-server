from typing import Annotated
import logging

from fastapi import FastAPI, Request, Depends, HTTPException, Response
from fastapi.responses import JSONResponse

from server.core.config import with_config_loader, with_config_parser
from server.core.routing import RouteMap, with_route_map
from server.core.metrics import MetricRecorder, with_metric_recorder

from .response_transformer import with_response_transformer, ResponseTransformer
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
async def get(request: Request,
              full_path: str,
              route_map: Annotated[RouteMap, Depends(with_route_map)],
              response_transformer: Annotated[ResponseTransformer, Depends(with_response_transformer)],
              metrics: Annotated[MetricRecorder, Depends(with_metric_recorder)]):

    if metrics.is_enabled() and full_path == '__metrics__':
        mets = metrics.get_metrics()
        _log.debug(f'Serving metrics [{mets}]')
        return JSONResponse(mets)

    entry = await route_map.find_entry_for_request(request)
    if entry is None:
        raise HTTPException(status_code=404, detail='No har entry matching request found.')
    return response_transformer.map_to_fastapi_response(entry)


@app.exception_handler(Exception)
def handle_exception(request: Request, exception: Exception):
    _log.error(f'Handling uncaught exception: [{exception}]')
    config_loader = with_config_loader(with_config_parser())
    if config_loader.get_app_config().debug.log_stack_traces:
        _log.exception(exception)
    return Response(status_code=500)
