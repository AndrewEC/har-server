import unittest
from unittest.mock import patch, Mock, MagicMock

from server.core.config import ConfigLoader, AppConfig
from server.core.config.models import Matchers
from server.core.har.models import RequestHashes
from server.core.rules.matching import RequestMatcher

from server.tests.util import fully_qualified_name


class RequestMatcherTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_find_matching_entry(self, mock_config_loader: ConfigLoader):

        hashes = RequestHashes(query_params='query', headers='hashes', cookies='cookies', post_data='post-data')
        different_hashes = RequestHashes(query_params='diff_query', headers='hashes', cookies='cookies', post_data='post-data')

        arguments = [
            (hashes, hashes, True),
            (hashes, different_hashes, False)
        ]

        for sub_arguments in arguments:
            with self.subTest(sub_arguments):
                all_rules = [
                    'method',
                    'path',
                    'query-params',
                    'headers',
                    'cookies',
                    'body'
                ]
                mock_config_loader.get_app_config = Mock(return_value=AppConfig(request_matching=Matchers(rules=all_rules)))

                har_entry = MagicMock(request=MagicMock(hashes=sub_arguments[0], path='/path', method='GET'))
                request = MagicMock(hashes=sub_arguments[1], path='/path', method='GET')

                request_matcher = RequestMatcher(mock_config_loader)
                request_matcher.prime([har_entry])

                actual = request_matcher.find_matching_entry(request)

                if sub_arguments[2]:
                    self.assertEqual(har_entry, actual)
                else:
                    self.assertIsNone(actual)

                mock_config_loader.get_app_config.assert_called_once()
