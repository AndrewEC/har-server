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
