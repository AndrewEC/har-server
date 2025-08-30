from functools import lru_cache
import base64

from fastapi import Response

from server.core.har import HarEntryResponse


class ResponseTransformer:

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
def with_response_transformer() -> ResponseTransformer:
    return ResponseTransformer()
