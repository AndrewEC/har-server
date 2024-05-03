from __future__ import annotations
from typing import Dict, Callable, List
from enum import Enum
import logging

from server.core.config import ConfigLoader
from server.core.config.models import ResponseRuleConfig
from server.core.har import HarEntryResponse


_log = logging.getLogger(__file__)

_EMPTY_PROTOCOL_START_TOKEN = '/'
_EMPTY_PROTOCOL_END_TOKEN = '/'

_HTTP_START_TOKEN = 'h'
_HTTP_PROTOCOL = 'http://'
_HTTP_PROTOCOL_LENGTH = len(_HTTP_PROTOCOL)
_HTTPS_PROTOCOL = 'https://'
_HTTPS_PROTOCOL_LENGTH = len(_HTTPS_PROTOCOL)

_LETTERS_MIN = ord('A')
_LETTERS_MAX = ord('z')
_NUMBERS_MIN = ord('0')
_NUMBERS_MAX = ord('9')
_DOT_CHARACTER = ord('.')
_HYPHEN_CHARACTER = ord('-')

_COLON_CHARACTER = ord(':')

_LOCALHOST = 'http://localhost:8080'


class _CaptorState(Enum):
    LOOKING_FOR_PROTOCOL = 1
    CAPTURING_EMPTY_PROTOCOL = 2
    CAPTURING_HTTP_PROTOCOL = 3
    CAPTURING_HTTPS_PROTOCOL = 4
    CAPTURING_HOST = 5
    CAPTURING_PORT = 6


class _CapturedOrigin:

    def __init__(self, start_index: int, length: int):
        self.start_index = start_index
        self.length = length


class _UrlOriginCaptor:

    def __init__(self):
        self._capture_functions: Dict[_CaptorState, Callable[[str, int], None]] = {
            _CaptorState.LOOKING_FOR_PROTOCOL: self._looking_for_protocol,
            _CaptorState.CAPTURING_EMPTY_PROTOCOL: self._capturing_empty_protocol,
            _CaptorState.CAPTURING_HTTP_PROTOCOL: self._capturing_http_protocol,
            _CaptorState.CAPTURING_HTTPS_PROTOCOL: self._capturing_https_protocol,
            _CaptorState.CAPTURING_HOST: self._capturing_host,
            _CaptorState.CAPTURING_PORT: self._capturing_port
        }

        self._capture_results: List[_CapturedOrigin] = []

        self._run_once = False

        self._start_index = -1
        self._captured_length = 0
        self._captured_something_for_host = False
        self._captured_dot_in_host = False
        self._captured_something_for_port = False
        self._current_capture_function = self._capture_functions[_CaptorState.LOOKING_FOR_PROTOCOL]

    def capture_origin_locations(self, value: str) -> _UrlOriginCaptor:
        if self._run_once:
            raise Exception('_UrlOriginCaptor.capture_origin_locations has already been invoked. Invoke fully_reset '
                            'to clear out last result set before invoking capture_origin_locations again.')
        self._run_once = True

        for index, value in enumerate(value):
            self._next_char(value, index)
        return self

    def get_capture_results(self) -> List[_CapturedOrigin]:
        return self._capture_results[:]

    def fully_reset(self):
        self._capture_results.clear()
        self._run_once = False
        self._reset()

    def _next_char(self, char: str, index: int):
        self._current_capture_function(char, index)

    def _next_state(self, state: _CaptorState):
        self._current_capture_function = self._capture_functions[state]

    def _character_captured(self):
        self._captured_length = self._captured_length + 1

    def _first_character_captured(self, index: int):
        self._start_index = index
        self._character_captured()

    def _origin_captured(self):
        self._capture_results.append(_CapturedOrigin(self._start_index, self._captured_length))
        self._reset()

    def _reset(self):
        self._start_index = -1
        self._captured_length = 0
        self._captured_something_for_host = False
        self._captured_dot_in_host = False
        self._captured_something_for_port = False
        self._next_state(_CaptorState.LOOKING_FOR_PROTOCOL)

    def _looking_for_protocol(self, char: str, index: int):
        if char == _HTTP_START_TOKEN:
            self._first_character_captured(index)
            self._next_state(_CaptorState.CAPTURING_HTTP_PROTOCOL)
        elif char == _EMPTY_PROTOCOL_START_TOKEN:
            self._first_character_captured(index)
            self._next_state(_CaptorState.CAPTURING_EMPTY_PROTOCOL)

    def _capturing_empty_protocol(self, char: str, index: int):
        if _EMPTY_PROTOCOL_END_TOKEN == char:
            self._character_captured()
            self._next_state(_CaptorState.CAPTURING_HOST)
        else:
            self._reset()

    def _capturing_http_protocol(self, char: str, index: int):
        if _HTTP_PROTOCOL[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTP_PROTOCOL_LENGTH:
                self._next_state(_CaptorState.CAPTURING_HOST)
        elif _HTTPS_PROTOCOL[self._captured_length] == char:
            self._next_state(_CaptorState.CAPTURING_HTTPS_PROTOCOL)
            self._character_captured()
        else:
            self._reset()

    def _capturing_https_protocol(self, char: str, index: int):
        if _HTTPS_PROTOCOL[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTPS_PROTOCOL_LENGTH:
                self._next_state(_CaptorState.CAPTURING_HOST)
        else:
            self._reset()

    def _capturing_host(self, char: str, index: int):
        char_value = ord(char)
        if _LETTERS_MIN <= char_value <= _LETTERS_MAX or _NUMBERS_MIN <= char_value <= _NUMBERS_MAX:
            self._captured_something_for_host = True
            self._character_captured()
        elif char_value == _DOT_CHARACTER:
            if not self._captured_something_for_host:
                self._reset()
            else:
                self._captured_dot_in_host = True
                self._character_captured()
        elif char_value == _HYPHEN_CHARACTER:
            if not self._captured_something_for_host:
                self._reset()
            else:
                self._character_captured()
        elif char_value == _COLON_CHARACTER:
            if self._captured_something_for_host and self._captured_dot_in_host:
                self._character_captured()
                self._next_state(_CaptorState.CAPTURING_PORT)
            else:
                self._reset()
        else:
            if self._captured_something_for_host and self._captured_dot_in_host:
                self._origin_captured()
            else:
                self._reset()

    def _capturing_port(self, char: str, index: int):
        char_value = ord(char)
        if _NUMBERS_MIN <= char_value <= _NUMBERS_MAX:
            self._captured_something_for_port = True
            self._character_captured()
        else:
            if self._captured_something_for_port:
                self._origin_captured()
            else:
                self._reset()


def _replace_captured_origin(content: str, captured: _CapturedOrigin, modifier: int, excluded_domains: List[str]) -> str:
    start_index = captured.start_index - modifier
    origin = content[start_index:start_index + captured.length]
    if origin in excluded_domains:
        return content
    _log.debug(f'Replacing with localhost: [{origin}]')
    return content[:start_index] + _LOCALHOST + content[start_index + captured.length:]


def _replace_all_captured_origins(content: str,
                                  capture_results: List[_CapturedOrigin],
                                  excluded_domains: List[str]) -> str:
    # The modifier is used to capture the change in the length of the input content string as each
    # captured domain is replaced with the localhost domain.
    modifier = 0
    for captured in capture_results:
        new_content = _replace_captured_origin(content, captured, modifier, excluded_domains)
        modifier = modifier + (len(content) - len(new_content))
        content = new_content
    return content


def rewrite_response_content_urls(config: ConfigLoader, response: HarEntryResponse) -> HarEntryResponse:
    content = response.content.text
    if content is None or len(content) == 0:
        return response

    capture_results = _UrlOriginCaptor().capture_origin_locations(content).get_capture_results()
    if len(capture_results) == 0:
        return response

    excluded_domains = config.read_config(ResponseRuleConfig).excluded_domains
    response.content.text = _replace_all_captured_origins(content, capture_results, excluded_domains)
    return response
