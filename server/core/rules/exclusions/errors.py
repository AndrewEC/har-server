class EntryExclusionRuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'A filter with the name [{}] could not be found.'

    def __init__(self, name: str):
        super().__init__(EntryExclusionRuleNotFoundException._MESSAGE_TEMPLATE.format(name))


class ExclusionRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The exclusion rule [{}] failed with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(ExclusionRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)
