from typing import List
from functools import lru_cache
from pathlib import Path
import json
import logging
import os
from threading import Lock

from server.core.config import get_root_path
from .models import HarFileContent, HarParseError


_log = logging.getLogger(__file__)


class HarParser:

    def __init__(self):
        self._har_file_contents = None
        self._lock = Lock()

    def get_har_file_contents(self) -> List[HarFileContent]:
        """
        Parses all the files within the har folder that have a .har extension.

        This will also search through nested directories to find addition files with the .har extension.

        This will cache the parsing results after the first invocation and will return the cached result
        on subsequent invocations.

        :return: The list of parsed har files. This will return the parsed har file content even if the har file
            did not contain any entries. (Meaning the file is effectively empty and won't change the behaviour of the
            har-server)
        :raise HarParseError: if an error occurs while parsing any of the har files. This error will contain
            the original error that caused the parsing to fail.
        """

        with self._lock:
            return self._do_get_har_file_contents()

    def _do_get_har_file_contents(self) -> List[HarFileContent]:
        if self._har_file_contents is not None:
            return self._har_file_contents

        parsed = []
        har_root_folder = get_root_path()
        _log.info(f'Parsing har files from folder: [{har_root_folder}]')
        for root, dirs, files in os.walk(har_root_folder):
            for file_name in files:
                if not file_name.endswith('.har'):
                    _log.info(f'Skipping file since it does not have a .har extension: [{file_name}]')
                    continue

                file_path = Path(root).joinpath(file_name)
                _log.info(f'Parsing har file: [{file_path}]')

                parsed_har_file = self._parse_har_file(file_path)
                if len(parsed_har_file.entries) == 0:
                    _log.info(f'Excluding har file since it has no entries: [{file_path}]')
                    continue

                parsed.append(parsed_har_file)

        self._har_file_contents = parsed

        return parsed

    def _do_parse_har_file(self, har_path: Path) -> HarFileContent:
        with open(har_path, 'r', encoding='utf-8') as file:
            contents = ''.join(file.readlines())
            return HarFileContent(har_path, json.loads(contents))

    def _parse_har_file(self, har_path: Path) -> HarFileContent:
        try:
            return self._do_parse_har_file(har_path)
        except Exception as e:
            raise HarParseError(f'Could not parse har file [{har_path}]', e) from e


@lru_cache()
def with_har_parser() -> HarParser:
    return HarParser()
