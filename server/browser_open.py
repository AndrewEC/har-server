from threading import Thread
from time import sleep
import webbrowser
import logging

from server.config import Config


_PORT_PLACEHOLDER = '${server.port}'

_log = logging.getLogger(__file__)


def _do_open_browser(url: str):
    sleep(0.2)
    webbrowser.open(url)


def open_browser_in_background(config: Config):
    if config.server.open is None:
        return
    url = config.server.open.replace(_PORT_PLACEHOLDER, str(config.server.port))
    _log.info(f'Browser will be opened to: [{url}]')
    Thread(target=_do_open_browser, args=(url,)).start()
