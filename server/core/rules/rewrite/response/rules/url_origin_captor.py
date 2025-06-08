from __future__ import annotations
from typing import List, Dict, Callable
from enum import Enum


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


class CapturedOrigin:

    def __init__(self, start_index: int, length: int):
        self.start_index = start_index
        self.length = length

    def copy(self) -> CapturedOrigin:
        return CapturedOrigin(self.start_index, self.length)


class UrlOriginCaptor:

    class _State(Enum):
        LOOKING_FOR_PROTOCOL = 1
        CAPTURING_EMPTY_PROTOCOL = 2
        CAPTURING_HTTP_PROTOCOL = 3
        CAPTURING_HTTPS_PROTOCOL = 4
        CAPTURING_HOST = 5
        CAPTURING_PORT = 6

    def __init__(self, value: str):
        self._capture_functions: Dict[UrlOriginCaptor._State, Callable[[str, int], None]] = {
            UrlOriginCaptor._State.LOOKING_FOR_PROTOCOL: self._looking_for_protocol,
            UrlOriginCaptor._State.CAPTURING_EMPTY_PROTOCOL: self._capturing_empty_protocol,
            UrlOriginCaptor._State.CAPTURING_HTTP_PROTOCOL: self._capturing_http_protocol,
            UrlOriginCaptor._State.CAPTURING_HTTPS_PROTOCOL: self._capturing_https_protocol,
            UrlOriginCaptor._State.CAPTURING_HOST: self._capturing_host,
            UrlOriginCaptor._State.CAPTURING_PORT: self._capturing_port
        }

        self._value = value

        self._capture_results: List[CapturedOrigin] = []

        self._run_once = False

        self._start_index = -1
        self._captured_length = 0
        self._captured_something_for_host = False
        self._captured_dot_in_host = False
        self._current_capture_function = self._capture_functions[UrlOriginCaptor._State.LOOKING_FOR_PROTOCOL]

    def capture_origin_locations(self) -> UrlOriginCaptor:
        if self._run_once:
            raise Exception('_UrlOriginCaptor.capture_origin_locations has already been invoked. '
                            'Use a new instance of _UrlOriginCaptor instead.')
        self._run_once = True

        for index, character in enumerate(self._value):
            self._current_capture_function(character, index)
        return self

    def get_capture_results(self) -> List[CapturedOrigin]:
        return [captured.copy() for captured in self._capture_results]

    def _reset(self):
        self._start_index = -1
        self._captured_length = 0
        self._captured_something_for_host = False
        self._captured_dot_in_host = False
        self._next_state(UrlOriginCaptor._State.LOOKING_FOR_PROTOCOL)

    def _next_state(self, state: UrlOriginCaptor._State):
        self._current_capture_function = self._capture_functions[state]

    def _character_captured(self):
        self._captured_length = self._captured_length + 1

    def _first_character_captured(self, index: int):
        self._start_index = index
        self._character_captured()

    def _origin_captured(self):
        last_character_index = self._start_index + self._captured_length - 1
        # To handle instances where there is a colon after the domain but no
        # port number.
        if (self._value[last_character_index] == ':'):
            self._captured_length -= 1
        self._capture_results.append(CapturedOrigin(self._start_index, self._captured_length))
        self._reset()

    def _looking_for_protocol(self, char: str, index: int):
        if char == _HTTP_START_TOKEN:
            self._first_character_captured(index)
            self._next_state(UrlOriginCaptor._State.CAPTURING_HTTP_PROTOCOL)
        elif char == _EMPTY_PROTOCOL_START_TOKEN:
            self._first_character_captured(index)
            self._next_state(UrlOriginCaptor._State.CAPTURING_EMPTY_PROTOCOL)

    def _capturing_empty_protocol(self, char: str, index: int):
        if _EMPTY_PROTOCOL_END_TOKEN == char:
            self._character_captured()
            self._next_state(UrlOriginCaptor._State.CAPTURING_HOST)
        else:
            self._reset()

    def _capturing_http_protocol(self, char: str, index: int):
        if _HTTP_PROTOCOL[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTP_PROTOCOL_LENGTH:
                self._next_state(UrlOriginCaptor._State.CAPTURING_HOST)
        elif _HTTPS_PROTOCOL[self._captured_length] == char:
            self._next_state(UrlOriginCaptor._State.CAPTURING_HTTPS_PROTOCOL)
            self._character_captured()
        else:
            self._reset()

    def _capturing_https_protocol(self, char: str, index: int):
        if _HTTPS_PROTOCOL[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTPS_PROTOCOL_LENGTH:
                self._next_state(UrlOriginCaptor._State.CAPTURING_HOST)
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
                self._next_state(UrlOriginCaptor._State.CAPTURING_PORT)
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
            self._character_captured()
        else:
            self._origin_captured()
