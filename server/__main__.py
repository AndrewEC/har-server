import base64

import click
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response

from server.parse import parse_har_files
from server.routes import RouteMap
from server.rewrite import apply_response_rules
from server.config import Config
from server.filter import apply_entry_filters

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
        raise HTTPException(status_code=404, detail='No matching request found.')

    _log.info(f'Found response for [{full_path}] within [{entry.parent.source_file.name}]')
    response = entry.response
    if response.content.encoding == 'base64':
        content = base64.b64decode(response.content.text)
        return Response(content=content, status_code=response.status, media_type=response.content.mime_type)
    else:
        response = apply_response_rules(config, entry.response)
        return Response(content=response.content.text, status_code=response.status, media_type=response.content.mime_type)


@click.command()
@click.argument('har')
def split_har(har: str):
    har_root_folder = Path(har)
    if not har_root_folder.is_dir():
        return print(f'The har argument must point to a directory containing a list of har files to be processed. '
                     f'Har path: [{har_root_folder}]')

    config.load(har_root_folder)

    har_file_contents = apply_entry_filters(config, parse_har_files(har_root_folder))

    if config.log_debug_info:
        log_debug_info(har_root_folder, har_file_contents)

    route_map.set_entries(har_file_contents)

    uvicorn.run(app, host='0.0.0.0', port=8000)


if __name__ == '__main__':
    split_har()
