import base64

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response

from server.parse import parse_har_files
from server.routes import RouteMap
from server.rewrite import apply_response_rewrite_rules
from server.config import Config
from server.exclusions import apply_entry_exclusions

from .logging_conf import *  # required to enable logging
from .debug import log_debug_info


_log = logging.getLogger(__file__)
app = FastAPI()
route_map = RouteMap()
config = Config()


@app.get('/{full_path:path}')
def get(request: Request, full_path: str):
    entry = route_map.find_entry_for_request(config, request)
    if entry is None:
        raise HTTPException(status_code=404, detail='No har entry matching request found.')

    _log.info(f'Request URL [{request.url}] matched to [{entry.request.url}] from .har file [{entry.parent.source_file.name}]')
    response = entry.response
    if response.content.encoding == 'base64':
        content = base64.b64decode(response.content.text)
        return Response(content=content, status_code=response.status, media_type=response.content.mime_type)
    else:
        response = apply_response_rewrite_rules(config, entry.response)
        return Response(
            content=response.content.text,
            status_code=response.status,
            media_type=response.content.mime_type,
            headers=response.headers
        )


@app.exception_handler(Exception)
def handle_exception(request: Request, exception: Exception):
    _log.error(f'Handling uncaught exception: [{exception}]')
    if config.debug.log_stack:
        _log.exception(exception)
    return Response(status_code=500)


@click.command()
@click.argument('har')
def split_har(har: str):
    har_root_folder = Path(har)
    if not har_root_folder.is_dir():
        return print(f'The har argument must point to a directory containing a list of har files to be processed. '
                     f'Har path: [{har_root_folder}]')

    config.load(har_root_folder)

    har_file_contents = apply_entry_exclusions(config, parse_har_files(har_root_folder))

    if config.debug.dump_urls:
        log_debug_info(har_root_folder, har_file_contents)

    route_map.set_entries(har_file_contents)

    uvicorn.run(app, host='0.0.0.0', port=config.port)


if __name__ == '__main__':
    split_har()
