from threading import Thread
from time import sleep
import webbrowser
import logging

from server.core.config import ConfigLoader
from server.core.config.models import Debug


_log = logging.getLogger(__file__)


def _do_open_browser(url: str):
    sleep(0.2)
    webbrowser.open(url)


def open_browser_in_background(config_loader: ConfigLoader):
    url = config_loader.read_config(Debug).open_browser
    if url is None:
        return
    _log.info(f'Browser will be opened to: [{url}]')
    Thread(target=_do_open_browser, args=(url,)).start()
