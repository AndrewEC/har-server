from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
from urllib.parse import unquote, urlparse
import json


def _parse_request_body(request: Dict[Any, Any]) -> Dict[Any, Any] | None:
    post_data = request.get('postData')
    if post_data is None:
        return None

    mimetype = post_data.get('mimeType')
    if mimetype is None:
        return

    if mimetype == 'application/json':
        text = post_data.get('text')
        return json.loads(text) if text is not None else None
    elif mimetype == 'application/x-www-form-urlencoded':
        params = post_data.get('params')
        if params is None:
            return None
        return {param['name']: param['value'] for param in params}

    return None


class HarParseError(Exception):

    def __init__(self, message: str, e: Exception):
        super().__init__(message, e)


class HarEntryRequest:

    def __init__(self, request: Dict[Any, Any]):
        self.method: str = request['method']
        self.url: str = request['url']
        self.path: str = unquote(urlparse(self.url).path)
        self.query_params: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['queryString']}
        self.headers: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['headers']}
        self.cookies: Dict[str, str] = {param['name'].lower(): param['value'] for param in request['cookies']}
        self.body = _parse_request_body(request)


class HarEntryResponseContent:

    def __init__(self, content: Dict[Any, Any]):
        self.mime_type: str | None = content.get('mimeType')
        self.encoding: str | None = content.get('encoding')
        self.text: str | None = content.get('text')


class HarEntryResponse:

    def __init__(self, response: Dict[Any, Any]):
        self.status: int = response['status']
        self.headers = {header['name'].lower(): header['value'] for header in response['headers']}
        self.content = HarEntryResponseContent(response['content'])
        self.cookies = {cookie['name'].lower(): cookie['value'] for cookie in response['cookies']}


class HarEntry:

    def __init__(self, parent: HarFileContent, entry: Dict[Any, Any]):
        self.parent = parent
        self.request = HarEntryRequest(entry['request'])
        self.response = HarEntryResponse(entry['response'])


class HarFileContent:

    def __init__(self, file: Path, contents: Dict[Any, Any]):
        self.source_file = file
        self.entries = [HarEntry(self, entry) for entry in contents['log']['entries']]
