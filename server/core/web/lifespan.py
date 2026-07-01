from contextlib import asynccontextmanager
from threading import Thread
import requests

from fastapi import FastAPI

from server.core.config import with_config_loader, with_config_parser
from server.core.debug import enable_debug_logs


def _send_initializing_request(port: int):
    requests.get(f'http://localhost:{port}')


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_config = with_config_loader(with_config_parser()).get_app_config()

    if app_config.debug.enable_debug_logs:
        enable_debug_logs()
    
    Thread(target=_send_initializing_request, args=(app_config.port,)).start()

    yield
