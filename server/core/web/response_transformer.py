from typing import Annotated
from functools import lru_cache
import base64

from fastapi import Response, Depends

from server.core.har import HarEntryResponse
from server.core.rules.rewrite.response import with_response_rewriter, ResponseRewriter


class ResponseTransformer:

    def __init__(self, response_rewriter: ResponseRewriter):
        self._response_rewriter = response_rewriter

    def map_to_fastapi_response(self, response: HarEntryResponse) -> Response:
        if response.content.encoding == 'base64':
            return self._map_base64_response(response)
        else:
            return self._map_text_response(response)

    def _map_base64_response(self, response: HarEntryResponse) -> Response:
        if response.content.text is not None:
            content = base64.b64decode(response.content.text)
        else:
            content = ''

        return Response(
            content=content,
            status_code=response.status,
            media_type=response.content.mime_type
        )

    def _map_text_response(self, response: HarEntryResponse) -> Response:
        response = self._response_rewriter.apply_response_rewrite_rules(response)
        api_response = Response(
            content=response.content.text,
            status_code=response.status,
            media_type=response.content.mime_type,
            headers=response.headers
        )
        for name, value in response.cookies.items():
            api_response.set_cookie(name, value)
        return api_response


@lru_cache()
def with_response_transformer(response_rewriter: Annotated[ResponseRewriter, Depends(with_response_rewriter)]) -> ResponseTransformer:
    return ResponseTransformer(response_rewriter)
