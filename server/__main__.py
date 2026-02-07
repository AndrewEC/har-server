from pathlib import Path

import click
import uvicorn

from server.core.config import set_root_path
from server.core.web import app

from server.logging_conf import configure_logging


@click.command()
@click.argument('har')
def run(har: str):
    configure_logging()
    har_folder = Path(har)
    if not har_folder.is_dir():
        return print('Har argument must point to a directory.')
    set_root_path(har_folder)

    uvicorn.run(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    run()
