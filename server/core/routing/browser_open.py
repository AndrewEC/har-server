from threading import Thread
from typing import Annotated
import webbrowser
import logging
from functools import lru_cache

from fastapi import Depends

from server.core.config import ConfigLoader
from server.core.config.config_loader import with_config_loader


_log = logging.getLogger(__file__)


class BrowserOpen:

    def __init__(self, config_loader: ConfigLoader):
        app_config = config_loader.get_app_config()
        self._url = app_config.open_browser
        if self._url is not None:
            self._url = self._url.replace('{port}', str(app_config.port))

    def _do_open_browser(self, url: str):
        webbrowser.open(url)

    def open_browser_in_background(self):
        if self._url is None:
            return
        _log.info(f'Launching browser with URL: [{self._url}]')
        Thread(target=self._do_open_browser, args=(self._url,)).start()


@lru_cache()
def with_browser_open(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> BrowserOpen:
    return BrowserOpen(config_loader)
