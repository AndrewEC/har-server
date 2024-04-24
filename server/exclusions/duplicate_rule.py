from typing import List

from server.parse import HarFileContent
from server.routes import do_requests_match
from server.config import Config


def _remove_duplicates_within_file(config: Config, content: HarFileContent):
    entry_count = len(content.entries)
    for i in range(entry_count):
        for j in range(entry_count):
            if i == j or content.entries[i] is None or content.entries[j] is None:
                continue
            if do_requests_match(config, content.entries[i].request, content.entries[j].request):
                content.entries[j] = None
    content.entries = list(filter(None, content.entries))


def _remove_content_across_files(config: Config, content: HarFileContent, all_contents: List[HarFileContent]):
    for second_content in all_contents:
        if content == second_content:
            continue
        for i in range(len(content.entries)):
            for j in range(len(second_content.entries)):
                if content.entries[i] is None or second_content.entries[j] is None:
                    continue
                if do_requests_match(config, content.entries[i].request, second_content.entries[j].request):
                    second_content.entries[j] = None
    content.entries = list(filter(None, content.entries))


def remove_duplicates_exclusion_rule(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    for content in file_contents:
        _remove_duplicates_within_file(config, content)
    for content in file_contents:
        _remove_content_across_files(config, content, file_contents)
    return file_contents
