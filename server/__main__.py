from pathlib import Path

import click
import uvicorn

from server.core.config import set_root_path, with_config_parser
from server.core.web import app

from server.logging_conf import configure_logging, logging


_DEFAULT_PORT = 8080

_log = logging.getLogger(__file__)


def _get_port() -> int:
    config = with_config_parser().parse_config_yml()
    if config is not None:
        return config.get('port', _DEFAULT_PORT)
    return _DEFAULT_PORT


@click.command()
@click.argument('har')
def run(har: str):

    configure_logging()

    har_folder = Path(har)
    if not har_folder.is_dir():
        return print('har argument must point to a directory.')
    set_root_path(har_folder)

    port = _get_port()
    _log.info(f'Starting server on port: [{port}].')
    uvicorn.run(app, host='0.0.0.0', port=port)


if __name__ == '__main__':
    run()
