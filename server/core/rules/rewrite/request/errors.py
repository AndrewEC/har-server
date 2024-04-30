class RequestRuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'No request rule with the name [{}] could be found.'

    def __init__(self, name: str):
        super().__init__(RequestRuleNotFoundException._MESSAGE_TEMPLATE.format(name))


class RequestRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The request rewrite rule [{}] finished with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(RequestRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)
