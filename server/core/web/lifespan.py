from contextlib import asynccontextmanager
from threading import Thread
import requests
from time import sleep

from fastapi import FastAPI

from server.core.config import with_config_loader, with_config_parser
from server.core.debug import enable_debug_logs


def _send_initializing_request():
    sleep(1)
    requests.get('http://localhost:8080')


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_loader = with_config_loader(with_config_parser())

    if config_loader.get_app_config().debug.enable_debug_logs:
        enable_debug_logs()
    
    Thread(target=_send_initializing_request).start()

    yield
