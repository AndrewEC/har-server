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
        if response.content.text != '':
            content = base64.b64decode(response.content.text)
        else:
            content = ''

        return Response(
            content=content,
            status_code=response.status,
            media_type=response.content.mime_type
        )

    def _map_text_response(self, response: HarEntryResponse) -> Response:
        headers = {header.name: header.value for header in response.headers}
        api_response = Response(
            content=response.content.text,
            status_code=response.status,
            media_type=response.content.mime_type,
            headers=headers
        )
        for cookie in response.cookies:
            api_response.set_cookie(cookie.name, cookie.value)
        return api_response


@lru_cache()
def with_response_transformer() -> ResponseTransformer:
    return ResponseTransformer()
