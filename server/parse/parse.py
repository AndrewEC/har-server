from typing import List
from pathlib import Path
import json
import logging

from .models import HarFileContent, HarParseError

_log = logging.getLogger(__file__)


def _do_parse_har_file(har_path: Path) -> HarFileContent:
    with open(har_path, 'r', encoding='utf-8') as file:
        contents = ''.join(file.readlines())
        return HarFileContent(har_path, json.loads(contents))


def _parse_har_file(har_path: Path) -> HarFileContent:
    try:
        return _do_parse_har_file(har_path)
    except Exception as e:
        raise HarParseError('Could not parse har file.', e)


def parse_har_files(har_root_folder: Path) -> List[HarFileContent]:
    parsed = []
    _log.info(f'Parsing har files from har folder: [{har_root_folder}]')
    for file in har_root_folder.iterdir():
        if not file.is_file():
            _log.info(f'Skipping path since it points to a directory: [{file}]')
            continue
        if not file.suffix == '.har':
            _log.info(f'Skipping file since it does not have a .har extension: [{file}]')
            continue
        _log.info(f'Parsing har file: [{file}]')
        parsed.append(_parse_har_file(file))
    return parsed
