class DuplicateRuleException(Exception):

    _MESSAGE_TEMPLATE = 'Duplicate rule of type [{}] registered with name [{}].'

    def __init__(self, container_name: str, name: str):
        super().__init__(DuplicateRuleException._MESSAGE_TEMPLATE.format(container_name, name))


class RuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'Could not find rule of type [{}] with name [{}].'

    def __init__(self, container_name: str, name: str):
        super().__init__(RuleNotFoundException._MESSAGE_TEMPLATE.format(container_name, name))


class RuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'Execution of rule [{}] of type [{}] failed with error [{}]'

    def __init__(self, container_name: str, name: str, cause: Exception):
        super().__init__(RuleFailedException._MESSAGE_TEMPLATE.format(name, container_name, cause))


class RuleInitializationFailed(Exception):

    _MESSAGE_TEMPLATE = 'Failed to initialize rule of type [{}] with name [{}]. Cause: [{}]'

    def __init__(self, container_name: str, name: str, cause: Exception):
        super().__init__(RuleInitializationFailed._MESSAGE_TEMPLATE.format(container_name, name, cause), cause)


class ContainerRulesAlreadyEnabled(Exception):

    _MESSAGE_TEMPLATE = 'Container [{}] rules have already been enabled.'

    def __init__(self, container_name: str):
        super().__init__(ContainerRulesAlreadyEnabled._MESSAGE_TEMPLATE.format(container_name))
