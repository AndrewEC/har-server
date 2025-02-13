class DuplicateRuleException(Exception):

    _MESSAGE_TEMPLATE = 'Two rules of type [{}] attempted to register with name [{}].'

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


class RuleInitializationFailedException(Exception):

    _MESSAGE_TEMPLATE = 'Failed to initialize rule of type [{}] with name [{}]. Cause: [{}]'

    def __init__(self, container_name: str, name: str, cause: Exception):
        super().__init__(RuleInitializationFailedException._MESSAGE_TEMPLATE.format(container_name, name, cause), cause)


class ContainerRulesAlreadyEnabledException(Exception):

    _MESSAGE_TEMPLATE = 'Container [{}] rules have already been enabled.'

    def __init__(self, container_name: str):
        super().__init__(ContainerRulesAlreadyEnabledException._MESSAGE_TEMPLATE.format(container_name))


class MissingConfigPropertyException(Exception):

    _MESSAGE_TEMPLATE = 'Rule [{}] has been enabled but the [{}] property has not been defined.'

    def __init__(self, rule_name: str, property_path: str):
        super().__init__(MissingConfigPropertyException._MESSAGE_TEMPLATE.format(rule_name, property_path))
