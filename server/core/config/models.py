from typing import List

from .prefix import prefix
from .post_construct import post_construct
from .functions import make_lowercase


@prefix('debug')
class Debug:
    enable_debug_logs = False
    dump_urls = False
    log_stack_traces = False
    open_browser: str | None = None


@prefix('request-matching')
class Matchers:
    rules: List[str] = []


# ===== ===== ===== Request Rewrite ===== ===== =====
@prefix('rewrite.request')
class RequestRewriteRules:
    rules: List[str] = []


@post_construct('post_construct')
@prefix('rewrite.request.config')
class RequestRewriteConfig:
    removable_cookies: List[str] = []
    removable_query_params: List[str] = []
    removable_headers: List[str] = []
    pre_apply: bool = False

    def post_construct(self):
        self.removable_cookies = make_lowercase(self.removable_cookies)
        self.removable_headers = make_lowercase(self.removable_headers)
        self.removable_query_params = make_lowercase(self.removable_query_params)
# ===== ===== ===== Request Rewrite ===== ===== =====


# ===== ===== ===== Response Rewrite ===== ===== =====
@prefix('rewrite.response')
class ResponseRewriteRules:
    rules: List[str] = []


@post_construct('post_construct')
@prefix('rewrite.response.config')
class ResponseRuleConfig:
    excluded_domains: List[str] = []
    removable_headers: List[str] = []
    removable_cookies: List[str] = []

    def post_construct(self):
        self.removable_headers = make_lowercase(self.removable_headers)
        self.removable_cookies = make_lowercase(self.removable_cookies)
# ===== ===== ===== Response Rewrite ===== ===== =====


# ===== ===== ===== Exclusions ===== ===== =====
@prefix('exclusions')
class ExclusionRules:
    rules: List[str] = []


@post_construct('post_construct')
@prefix('exclusions.config')
class ExclusionConfig:
    removable_statuses: List[int] = []
    removable_http_methods: List[str] = []
    pre_apply: bool = False

    def post_construct(self):
        self.removable_http_methods = make_lowercase(self.removable_http_methods)
# ===== ===== ===== Exclusions ===== ===== =====
