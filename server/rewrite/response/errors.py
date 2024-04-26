class ResponseRuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'No response rule with the name [{}] could be found.'

    def __init__(self, name: str):
        super().__init__(ResponseRuleNotFoundException._MESSAGE_TEMPLATE.format(name))


class ResponseRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The response rewrite rule [{}] finished with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(ResponseRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)
