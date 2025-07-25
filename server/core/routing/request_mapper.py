from typing import Dict, List, Any
from functools import lru_cache
import logging

from fastapi import Request

from server.core.har import HarEntryRequest


_log = logging.getLogger(__file__)


class RequestMapper:

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
        if len(request_body) > 0 and self._is_json_request_body(request_options):
            request_options['postData'] = {
                'text': request_body,
                'mimeType': 'application/json'
            }

        _log.debug(f'Mapping request options to har entry: [{request_options}]')

        return HarEntryRequest(request_options)

    def _is_json_request_body(self, request: Dict[str, Any]) -> bool:
        headers = request['headers']
        content_type_header = next((header for header in headers if 'content-type' == header['name'].lower()), None)
        return content_type_header is not None and 'application/json' in content_type_header['value']


@lru_cache()
def with_request_mapper() -> RequestMapper:
    return RequestMapper()
