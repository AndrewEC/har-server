from typing import Dict, Callable, List
from enum import Enum

from server.config import Config
from server.parse import HarEntryResponse


_START_TOKEN = 'h'
_HTTP_PREFIX = 'http://'
_HTTP_PREFIX_LENGTH = len(_HTTP_PREFIX)
_HTTPS_PREFIX = 'https://'
_HTTPS_PREFIX_LENGTH = len(_HTTPS_PREFIX)
_HOST_CHARACTERS_MIN = ord('A')
_HOST_CHARACTERS_MAX = ord('z')
_HOST_CHARACTER_NUMBER_MIN = ord('0')
_HOST_CHARACTER_NUMBER_MAX = ord('9')
_HOST_CHARACTERS_DOT = ord('.')
_HOST_CHARACTERS_HYPHEN = ord('-')
_LOCALHOST = 'http://localhost:8000'


class _CaptorState(Enum):
    LOOKING_FOR_PREFIX = 1
    CAPTURING_PREFIX = 2
    CAPTURING_HTTPS_PREFIX = 3
    CAPTURING_HOST = 4


class _Captured:

    def __init__(self, start_index: int, length: int):
        self.start_index = start_index
        self.length = length


class _ChangeResult:

    def __init__(self, content: str, length_change: int):
        self.content = content
        self.length_change = length_change


class _Captor:

    def __init__(self):
        self._start_index = -1
        self._captured_length = 0
        self.captured: List[_Captured] = []
        self._capture_functions: Dict[_CaptorState, Callable[[str, int], None]] = {
            _CaptorState.LOOKING_FOR_PREFIX: self._on_waiting,
            _CaptorState.CAPTURING_PREFIX: self._on_capturing_prefix,
            _CaptorState.CAPTURING_HTTPS_PREFIX: self._on_capturing_https_prefix,
            _CaptorState.CAPTURING_HOST: self._on_capturing_host
        }
        self._current_capture_function = self._capture_functions[_CaptorState.LOOKING_FOR_PREFIX]

    def _update_state(self, state: _CaptorState):
        self._current_capture_function = self._capture_functions[state]

    def next_char(self, char: str, index: int):
        self._current_capture_function(char, index)

    def _character_captured(self):
        self._captured_length = self._captured_length + 1

    def _clear(self):
        self._captured_length = 0
        self._start_index = 0
        self._update_state(_CaptorState.LOOKING_FOR_PREFIX)

    def _on_waiting(self, char: str, index: int):
        if char == _START_TOKEN:
            self._start_index = index
            self._character_captured()
            self._update_state(_CaptorState.CAPTURING_PREFIX)

    def _on_capturing_prefix(self, char: str, index: int):
        if _HTTP_PREFIX[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTP_PREFIX_LENGTH:
                self._update_state(_CaptorState.CAPTURING_HOST)
        elif _HTTPS_PREFIX[self._captured_length] == char:
            self._update_state(_CaptorState.CAPTURING_HTTPS_PREFIX)
            self._character_captured()
        else:
            self._clear()

    def _on_capturing_https_prefix(self, char: str, index: int):
        if _HTTPS_PREFIX[self._captured_length] == char:
            self._character_captured()
            if self._captured_length == _HTTPS_PREFIX_LENGTH:
                self._update_state(_CaptorState.CAPTURING_HOST)
        else:
            self._clear()

    def _on_capturing_host(self, char: str, index: int):
        char_value = ord(char)
        if (_HOST_CHARACTERS_MIN <= char_value <= _HOST_CHARACTERS_MAX
                or _HOST_CHARACTER_NUMBER_MIN <= char_value <= _HOST_CHARACTER_NUMBER_MAX
                or char_value == _HOST_CHARACTERS_DOT
                or char_value == _HOST_CHARACTERS_HYPHEN):
            self._character_captured()
        else:
            self.captured.append(_Captured(self._start_index, self._captured_length))
            self._clear()


def _modify_text(content: str, captured: _Captured, modifier: int, config: Config) -> str:
    start_index = captured.start_index - modifier
    domain = content[start_index:start_index + captured.length]
    if domain in config.rewrite_rules.rule_config.excluded_domains:
        return content
    return content[:start_index] + _LOCALHOST + content[start_index + captured.length:]


def rewrite_response_content_urls(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    content = response.content.text
    captor = _Captor()
    for index, value in enumerate(content):
        captor.next_char(value, index)

    modifier = 0
    for captured in captor.captured:
        new_content = _modify_text(content, captured, modifier, config)
        modifier = modifier + (len(content) - len(new_content))
        content = new_content

    response.content.text = content
    return response
