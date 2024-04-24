class MatchRuleNotFound(Exception):

    _MESSAGE_TEMPLATE = 'Could not find request matcher named [{}].'

    def __init__(self, name: str):
        super().__init__(MatchRuleNotFound._MESSAGE_TEMPLATE.format(name))


class MatchRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The match rule [{}] failed with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(MatchRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)
