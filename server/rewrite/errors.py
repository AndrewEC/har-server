class RuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'No {} rule with the name [{}] could be found.'

    def __init__(self, rule_type: str, name: str):
        super().__init__(RuleNotFoundException._MESSAGE_TEMPLATE.format(rule_type, name))


class ResponseRuleNotFoundException(RuleNotFoundException):

    def __init__(self, name: str):
        super().__init__('response', name)


class RequestRuleNotFoundException(RuleNotFoundException):

    def __init__(self, name: str):
        super().__init__('request', name)


class RequestRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The request rewrite rule [{}] finished with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(RequestRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)


class ResponseRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The response rewrite rule [{}] finished with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(ResponseRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)
