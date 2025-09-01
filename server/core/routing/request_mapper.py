from typing import Dict, List, Any
from functools import lru_cache
import logging
import urllib.parse

from fastapi import Request

from server.core.har import HarEntryRequest


_log = logging.getLogger(__file__)


class RequestMapper:

    _APPLICATION_JSON_CONTENT_TYPE = 'application/json'
    _FORM_URL_ENCODED_CONTENT_TYPE = 'application/x-www-form-urlencoded'

    async def map_to_har_request(self, request: Request) -> HarEntryRequest:
        """
        Maps an incoming FastAPI request object to a har entry request. This will copy over the
        query params, headers, cookies, http method, json body, and url.

        :param request: The incoming FastAPI Http request.
        :return: The har entry request object.
        """

        query_params: List[Dict[str, str | None]] = [{'name': key, 'value': request.query_params.get(key)} for key in request.query_params.keys()]
        headers: List[Dict[str, str | None]] = [{'name': key, 'value': request.headers.get(key)} for key in request.headers.keys()]
        cookies: List[Dict[str, str | None]] = [{'name': key, 'value': request.cookies.get(key)} for key in request.cookies.keys()]

        request_options: Dict[str, Any] = {
            'queryString': query_params,
            'method': request.method,
            'url': str(request.url),
            'headers': headers,
            'cookies': cookies
        }

        request_body = await request.body()
        if len(request_body) > 0:
            if self._has_json_body(request_options):
                request_options['postData'] = {
                    'text': request_body,
                    'mimeType': RequestMapper._APPLICATION_JSON_CONTENT_TYPE
                }
            elif self._has_form_url_encoded_body(request_options):
                request_options['postData'] = {
                    'text': request_body,
                    'params': self._parse_form_url_encoded_body(request_body),
                    'mimeType': RequestMapper._FORM_URL_ENCODED_CONTENT_TYPE
                }

        _log.debug(f'Mapping request options to har entry: [{request_options}]')

        return HarEntryRequest(request_options)

    def _parse_form_url_encoded_body(self, request_body: bytes) -> List[Dict[str, str]]:
        decoded_url_params = request_body.decode('utf-8')
        decoded_request_body = dict(urllib.parse.parse_qsl(decoded_url_params, keep_blank_values=True))
        return [{'name': key, 'value': value} for key, value in decoded_request_body.items()]

    def _has_json_body(self, request: Dict[str, Any]) -> bool:
        return self._has_content_type(request, RequestMapper._APPLICATION_JSON_CONTENT_TYPE)

    def _has_form_url_encoded_body(self, request: Dict[str, Any]) -> bool:
        return self._has_content_type(request, RequestMapper._FORM_URL_ENCODED_CONTENT_TYPE)

    def _has_content_type(self, request: Dict[str, Any], content_type: str) -> bool:
        content_type_header = self._get_header(request['headers'], 'content-type')
        return content_type_header is not None and content_type in content_type_header

    def _get_header(self, headers: List[Dict[str, str | None]], name: str) -> str | None:
        for header in headers:
            header_name = header.get('name')
            if header_name and header_name.lower() == name:
                return header['value']
        return None


@lru_cache()
def with_request_mapper() -> RequestMapper:
    return RequestMapper()
