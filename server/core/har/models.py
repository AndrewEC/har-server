from __future__ import annotations
from typing import Any, List, Dict
from urllib.parse import unquote, urlparse
import uuid
import json

from pydantic import BaseModel, ConfigDict, Field


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


class HarEntryRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)  # type: ignore

    method: str
    url: str
    path: str | None = None
    query_params: List[NameValuePair] = Field(alias='queryString')
    headers: List[NameValuePair]
    cookies: List[NameValuePair]
    post_data: RequestPostData = Field(alias='postData', default=RequestPostData())

    def model_post_init(self, context: Any):
        self.path = unquote(urlparse(self.url).path)
        self.method = self.method.lower()


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
