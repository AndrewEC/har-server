from __future__ import annotations
from typing import Any, List, Dict
from urllib.parse import unquote, urlparse
import uuid
import json

from pydantic import BaseModel, ConfigDict, Field


class SupportedBodyContentTypes:
    APPLICATION_JSON = 'application/json'
    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'


class HarParseError(Exception):

    def __init__(self, message: str, e: Exception):
        super().__init__(message, e)


class NameValuePair(BaseModel):
    name: str
    value: str

    def model_post_init(self, context: Any):
        self.name = self.name.lower()


class RequestPostData(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore

    mime_type: str = Field(alias='mimeType', default='')
    params: List[NameValuePair] = []
    text: str = ''
    parsed_json: Dict[str, Any] = {}

    def model_post_init(self, context: Any):
        self.mime_type = self.mime_type.lower()
        if 'application/json' in self.mime_type:
            self.parsed_json = json.loads(self.text)


class RequestHashes(BaseModel):
    query_params: str = ''
    headers: str = ''
    cookies: str = ''
    post_data: str = ''


class HarEntryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore

    method: str
    url: str
    path: str | None = None
    query_params: List[NameValuePair] = Field(alias='queryString')
    headers: List[NameValuePair]
    cookies: List[NameValuePair]
    post_data: RequestPostData = Field(alias='postData', default=RequestPostData())

    hashes: RequestHashes = Field(exclude=True, default=RequestHashes())

    def model_post_init(self, context: Any):
        self.path = unquote(urlparse(self.url).path)
        self.method = self.method.lower()
        self.compute_hashes()

    def compute_hashes(self):
        self.hashes = _hash_request_properties(self)


class ResponseContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore

    mime_type: str = Field(alias='mimeType', default='')
    encoding: str = ''
    text: str = ''


class HarEntryResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore

    status: int
    headers: List[NameValuePair]
    cookies: List[NameValuePair]
    content: ResponseContent


class HarEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore
    id: str = ''
    request: HarEntryRequest
    response: HarEntryResponse

    def model_post_init(self, context: Any):
        if self.id == '':
            self.id = str(uuid.uuid4())


class Log(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore
    entries: List[HarEntry]


class HarFileContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore
    log: Log


def _hash_pairs(pairs: List[NameValuePair]) -> str:
    if len(pairs) == 0:
        return ''

    sorted_pairs = sorted(pairs, key=lambda x: x.name)
    pairs_string = '&'.join([f'{pair.name}={pair.value}' for pair in sorted_pairs])
    return str(hash(pairs_string))


def _hash_body(request: HarEntryRequest) -> str:
    if request.post_data.mime_type == SupportedBodyContentTypes.APPLICATION_JSON:
        json_text = json.dumps(request.post_data.parsed_json, sort_keys=True)
        return str(hash(json_text))
    elif request.post_data.mime_type == SupportedBodyContentTypes.FORM_URL_ENCODED:
        return _hash_pairs(request.post_data.params)
    return ''


def _hash_request_properties(request: HarEntryRequest) -> RequestHashes:
    hashes: Dict[str, str] = dict()

    hashes['query_params'] = _hash_pairs(request.query_params)
    hashes['headers'] = _hash_pairs(request.headers)
    hashes['cookies'] = _hash_pairs(request.cookies)
    hashes['post_data'] = _hash_body(request)

    return RequestHashes(**hashes)
