from typing import List
from pathlib import Path
import logging

from server.parse import HarFileContent


_log = logging.getLogger(__file__)
_LOG_FILE = '_request_urls.txt'


def _form_source_file(file: HarFileContent) -> str:
    return f'===== {file.source_file} =====\n'


def log_debug_info(har_root_path: Path, file_contents: List[HarFileContent]):
    output_path = har_root_path.joinpath(_LOG_FILE)
    _log.info(f'Writing debug info to: [{output_path}]')

    with open(output_path, 'w') as file:
        for file_content in file_contents:
            file.write(_form_source_file(file_content))
            for entry in file_content.entries:
                file.write(f'\t{entry.request.method} {entry.request.url}\n')
            file.write('\n')
