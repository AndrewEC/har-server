from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from urllib.parse import unquote, urlparse
import json


def _get_or_none(options: Dict, key: str) -> Any | None:
    return options[key] if key in options else None


def _parse_request_body(request: Dict) -> Dict | None:
    post_data = _get_or_none(request, 'postData')
    if post_data is None:
        return None

    mimetype = _get_or_none(post_data, 'mimeType')
    if mimetype is None or mimetype != 'application/json':
        return

    text = _get_or_none(post_data, 'text')
    return json.loads(text) if text is not None else None


class HarParseError(Exception):

    def __init__(self, message: str, e: Exception):
        super().__init__(message, e)


class HarEntryRequest:

    def __init__(self, request: Dict):
        self.method: str = request['method']
        self.url: str = request['url']
        self.path: str = unquote(urlparse(self.url).path)
        self.query_params: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['queryString']}
        self.headers: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['headers']}
        self.cookies: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['cookies']}
        self.body = _parse_request_body(request)


class HarEntryResponseContent:

    def __init__(self, content: Dict):
        self.mime_type: str | None = _get_or_none(content, 'mimeType')
        self.encoding: str | None = _get_or_none(content, 'encoding')
        self.text: str | None = _get_or_none(content, 'text')


class HarEntryResponse:

    def __init__(self, response: Dict):
        self.status: int = response['status']
        self.headers = {header['name'].lower(): header['value'] for header in response['headers']}
        self.content = HarEntryResponseContent(response['content'])
        self.cookies = {cookie['name'].lower(): cookie['value'] for cookie in response['cookies']}


class HarEntry:

    def __init__(self, parent: HarFileContent, entry: Dict):
        self.parent = parent
        self.request = HarEntryRequest(entry['request'])
        self.response = HarEntryResponse(entry['response'])


class HarFileContent:

    def __init__(self, file: Path, contents: Dict):
        self.source_file = file
        self.title: str = contents['log']['pages'][0]['title']
        self.entries = [HarEntry(self, entry) for entry in contents['log']['entries']]
