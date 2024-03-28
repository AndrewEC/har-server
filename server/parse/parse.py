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
        raise HarParseError(f'Could not parse har file [{har_path}]', e)


def parse_har_files(har_root_folder: Path) -> List[HarFileContent]:
    """
    Parses all the files within the har_root_folder that have a .har extension.

    This will only parse .har files at the root of the har_root_folder directory. This will not attempt
    to traverse and scan any directories nested within the har_root_folder.

    :param har_root_folder: The path to the folder where all the .har files are contained.
    :return: The list of parsed har files. This will return the parsed har file content event if the har file
        did not contain any entries. (Meaning the file is effectively empty and won't change the behaviour of the
        har-server)
    :raise: HarParseError if an error occurs while parsing any of the har files. This error will contain the original
        error that caused the parsing to fail.
    """

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
