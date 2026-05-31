from typing import Generator
from functools import lru_cache
from pathlib import Path
import json
import logging
import os

from server.core.config import get_root_path
from .models import HarFileContent, HarParseError


_log = logging.getLogger(__file__)


class HarParser:

    def get_har_file_contents(self) -> Generator[HarFileContent, None, None]:
        """
        Parses and returns the contents of a .har file one by one.

        This will also search through nested directories to find addition files with the .har extension.

        :return: The list of parsed har files. This will not yield any entries if the .har file
            does not contain any entries.
        :raise HarParseError: if an error occurs while parsing any of the har files. This error will contain
            the original error that caused the parsing to fail.
        """

        har_root_folder = get_root_path()
        _log.info(f'Parsing har files from folder: [{har_root_folder}]')
        for root, _, files in os.walk(har_root_folder):
            for file_name in files:
                if not file_name.endswith('.har'):
                    _log.info(f'Skipping file since it does not have a .har extension: [{file_name}]')
                    continue

                file_path = Path(root).joinpath(file_name)
                _log.info(f'Parsing har file: [{file_path}]')

                parsed_har_file = self._parse_har_file(file_path)
                if len(parsed_har_file.log.entries) == 0:
                    _log.info(f'Excluding har file since it has no entries: [{file_path}]')
                    continue

                yield parsed_har_file

    def _parse_har_file(self, har_path: Path) -> HarFileContent:
        try:
            return self._do_parse_har_file(har_path)
        except Exception as e:
            raise HarParseError(f'Could not parse har file [{har_path}]', e) from e
    
    def _do_parse_har_file(self, har_path: Path) -> HarFileContent:
        with open(har_path, 'r', encoding='utf-8') as file:
            contents = ''.join(file.readlines())
            return HarFileContent(**json.loads(contents))


@lru_cache()
def with_har_parser() -> HarParser:
    return HarParser()
