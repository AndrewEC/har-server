from functools import lru_cache

from fastapi import Request

from server.core.har import HarEntryRequest


class RequestMapper:

    def map_to_har_request(self, request: Request) -> HarEntryRequest:
        """
        Maps an incoming FastAPI request object to a har entry request. This will copy over the
        query params, headers, cookies, http method, and url.

        :param request: The incoming FastAPI Http request.
        :return: The har entry request object.
        """

        query_params = [{'name': key, 'value': request.query_params.get(key)} for key in request.query_params.keys()]
        headers = [{'name': key, 'value': request.headers.get(key)} for key in request.headers.keys()]
        cookies = [{'name': key, 'value': request.cookies.get(key)} for key in request.cookies.keys()]
        request_options = {
            'queryString': query_params,
            'method': request.method,
            'url': str(request.url),
            'headers': headers,
            'cookies': cookies
        }
        return HarEntryRequest(request_options)


@lru_cache()
def with_request_mapper() -> RequestMapper:
    return RequestMapper()
