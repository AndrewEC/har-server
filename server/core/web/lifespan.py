from contextlib import asynccontextmanager

from fastapi import FastAPI

from server.core.config import with_config_loader, with_config_parser
from server.core.debug import enable_debug_logs

from .browser_open import open_browser_in_background


@asynccontextmanager
async def lifespan(app: FastAPI):
    config_loader = with_config_loader(with_config_parser())

    if config_loader.get_app_config().debug.enable_debug_logs:
        enable_debug_logs()

    open_browser_in_background(config_loader)

    yield
