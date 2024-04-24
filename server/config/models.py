from typing import List, TypeVar


T = TypeVar('T')


def _either(value: T | None, default: T) -> T:
    return value if value is not None else default


def _lowercase(value: List[str] | None) -> T:
    return [element.lower() for element in _either(value, [])]


class RewriteRulesConfig:

    def __init__(self,
                 excluded_domains: List[str] | None = None,
                 removable_query_params: List[str] | None = None,
                 removable_request_headers: List[str] | None = None,
                 removable_response_headers: List[str] | None = None,
                 removable_request_cookies: List[str] | None = None,
                 removable_response_cookies: List[str] | None = None):

        self.excluded_domains = _either(excluded_domains, [])
        self.removable_query_params = _lowercase(removable_query_params)
        self.removable_request_headers = _lowercase(removable_request_headers)
        self.removable_response_headers = _lowercase(removable_response_headers)
        self.removable_request_cookies = _lowercase(removable_request_cookies)
        self.removable_response_cookies = _lowercase(removable_response_cookies)


class ConfiguredRewriteRules:

    def __init__(self,
                 response_rules: List[str] | None = None,
                 request_rules: List[str] | None = None,
                 rule_config: RewriteRulesConfig = RewriteRulesConfig()):

        self.response_rules = _either(response_rules, [])
        self.request_rules = _either(request_rules, [])
        self.rule_config = rule_config


class ExclusionConfig:

    def __init__(self, removable_statuses: List[int] | None = None):
        self.removable_statuses = _either(removable_statuses, [])


class ConfiguredExclusions:

    def __init__(self, rules: List[str] | None = None, exclusion_config: ExclusionConfig = ExclusionConfig()):
        self.rules = _either(rules, [])
        self.exclusion_config = exclusion_config


class MatchConfig:

    def __init__(self):
        pass


class Matching:

    def __init__(self, rules: List[str] | None = None, match_config: MatchConfig = MatchConfig()):
        self.rules = _either(rules, [])
        self.match_config = match_config


class Server:

    def __init__(self, port=8080, open: str = None):
        self.port = port
        self.open = open


class Debug:

    def __init__(self, log_stack=False, dump_urls=False, enable_debug_logs=False):
        self.log_stack = log_stack
        self.dump_urls = dump_urls
        self.enable_debug_logs = enable_debug_logs
