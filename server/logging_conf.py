from pathlib import Path
import logging
import logging.config

def configure_logging():
    _LOGGING_CONFIG_PATH = Path(__file__).parent.parent.joinpath('logging.conf').absolute()
    if not _LOGGING_CONFIG_PATH.is_file():
        raise Exception(f'Could not find logging configuration file at: [{_LOGGING_CONFIG_PATH}]')
    logging.config.fileConfig(_LOGGING_CONFIG_PATH, disable_existing_loggers=False)

