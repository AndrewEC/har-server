from pathlib import Path

from server.core.config import set_root_path, get_root_path
from server.core.har import with_har_parser
from server.core.config import with_config_loader, with_config_parser
from server.core.rules.exclusions import with_exclusion_filter
from server.core.rules.matching import with_request_matcher
from server.core.rules.rewrite.response import with_response_rewriter
from server.core.rules.rewrite.request import with_request_rewriter


_CACHES = [
    with_har_parser,
    with_config_loader,
    with_exclusion_filter,
    with_request_matcher,
    with_response_rewriter,
    with_request_rewriter,
    with_config_parser
]


class TestData:

    def __init__(self, folder_name: str):
        self._test_data_path = Path(__file__).absolute().parent.joinpath('test_data').joinpath(folder_name)
        if not self._test_data_path.is_dir():
            raise Exception(f'Could not find test data path: [{self._test_data_path}].')
        self._last_root_path = get_root_path()

    def __enter__(self):
        set_root_path(self._test_data_path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_root_path(self._last_root_path)
        for cache in _CACHES:
            cache.cache_clear()
