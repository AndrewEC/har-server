from typing import List, Any

from pydantic import BaseModel

from .functions import make_lowercase


class Debug(BaseModel):
    enable_debug_logs: bool = False
    log_stack_traces: bool = False
    open_browser: str | None = None


class Matchers(BaseModel):
    rules: List[str] = []


# ===== ===== ===== Request Rewrite ===== ===== =====
class RequestRewriteConfig(BaseModel):
    removable_cookies: List[str] = []
    removable_query_params: List[str] = []
    removable_headers: List[str] = []
    pre_apply: bool = False

    def model_post_init(self, context: Any):
        self.removable_cookies = make_lowercase(self.removable_cookies)
        self.removable_headers = make_lowercase(self.removable_headers)
        self.removable_query_params = make_lowercase(self.removable_query_params)


class RequestRewriteRules(BaseModel):
    rules: List[str] = []

    config: RequestRewriteConfig = RequestRewriteConfig()
# ===== ===== ===== Request Rewrite ===== ===== =====


# ===== ===== ===== Response Rewrite ===== ===== =====
class ResponseRuleConfig(BaseModel):
    excluded_domains: List[str] = []
    removable_headers: List[str] = []
    removable_cookies: List[str] = []

    def model_post_init(self, context: Any):
        self.removable_headers = make_lowercase(self.removable_headers)
        self.removable_cookies = make_lowercase(self.removable_cookies)


class ResponseRewriteRules(BaseModel):
    rules: List[str] = []

    config: ResponseRuleConfig = ResponseRuleConfig()
# ===== ===== ===== Response Rewrite ===== ===== =====


# ===== ===== ===== Exclusions ===== ===== =====
class ExclusionConfig(BaseModel):
    removable_statuses: List[int] = []
    removable_http_methods: List[str] = []
    pre_apply: bool = False
    exclude_duplicate_requests: bool = False

    def model_post_init(self, context: Any):
        self.removable_http_methods = make_lowercase(self.removable_http_methods)


class ExclusionRules(BaseModel):
    rules: List[str] = []
    config: ExclusionConfig = ExclusionConfig()
# ===== ===== ===== Exclusions ===== ===== =====


class Rewrite(BaseModel):
    request: RequestRewriteRules = RequestRewriteRules()
    response: ResponseRewriteRules = ResponseRewriteRules()


class AppConfig(BaseModel):

    debug: Debug = Debug()
    request_matching: Matchers = Matchers()
    rewrite: Rewrite = Rewrite()
    exclusions: ExclusionRules = ExclusionRules()
