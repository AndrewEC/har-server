from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.core.config import with_config_loader, with_config_parser
from server.core.config.models import Debug
from server.core.debug import enable_debug_logs
from server.core.har import with_har_parser

from .browser_open import open_browser_in_background


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_loader = with_config_loader(with_config_parser())

    if config_loader.read_config(Debug).enable_debug_logs:
        enable_debug_logs()

    open_browser_in_background(config_loader)

    with_har_parser().get_har_file_contents()

    yield
