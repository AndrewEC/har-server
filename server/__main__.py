import click
import uvicorn

from server.config import set_root_path
from server.web import app

from .logging_conf import *  # Required to enable logging


@click.command()
@click.argument('har')
def run(har: str):
    har_folder = Path(har)
    if not har_folder.is_dir():
        return print('Har argument must point to a directory.')
    set_root_path(har_folder)

    uvicorn.run(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    run()
