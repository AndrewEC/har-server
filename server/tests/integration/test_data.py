from typing import Any, List, Type
from pathlib import Path
from types import TracebackType

from server.core.config import set_root_path, get_root_path, reset_config_loader, reset_config_parser
from server.core.har import with_har_parser
from server.core.rules.exclusions import with_exclusion_filter
from server.core.rules.matching import with_request_matcher
from server.core.rules.rewrite.response import with_response_rewriter
from server.core.rules.rewrite.request import with_request_rewriter


_CACHES: List[Any] = [
    with_har_parser,
    with_exclusion_filter,
    with_request_matcher,
    with_response_rewriter,
    with_request_rewriter,
]


class TestData:

    class DataSets:
        JSON_REQUEST_MATCHING = 'json_request_matching'
        FORM_REQUEST_MATCHING = 'form_request_matching'
        REWRITE_RESPONSE = 'rewrite_response'
        METRICS = 'metrics'

    def __init__(self, folder_name: str):
        self._test_data_path = Path(__file__).absolute().parent.joinpath('test_data').joinpath(folder_name)
        if not self._test_data_path.is_dir():
            raise Exception(f'Could not find test data path: [{self._test_data_path}].')
        self._last_root_path = get_root_path()

    def __enter__(self):
        set_root_path(self._test_data_path)

    def __exit__(self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None):
        set_root_path(self._last_root_path)
        for cache in _CACHES:
            cache.cache_clear()
        reset_config_loader()
        reset_config_parser()
