import logging


_log = logging.getLogger(__file__)


def enable_debug_logs():
    _log.info('Enabling debug level for logs.')
    logging.getLogger().setLevel(logging.DEBUG)
    for handler in logging.getLogger().handlers:
        handler.setLevel(logging.DEBUG)
