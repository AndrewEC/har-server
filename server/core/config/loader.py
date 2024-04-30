from typing import Type, TypeVar, Dict, Any
from functools import lru_cache
import logging
import yaml
import copy

from .functions import make_string
from .root import get_root_path
from .prefix import get_prefix
from .post_construct import get_post_construct_name, MissingPostConstructMethod


T = TypeVar('T')
_log = logging.getLogger(__file__)


class ConfigLoader:

    def __init__(self):
        self._configs: Dict[Type, Any] = {}
        self._parsed_yml = self._parse_config_yml()

    def read_config(self, model_type: Type[T]) -> T:
        """
        Instantiates the model_type and populates it with values pulled from the globally
        parsed yaml file. This will always return a copy of the instantiated and populated model.

        The model_type must be decorated with the '@prefix' decorator. The full path to each property
        being read from the yaml config file will be a combination of the string specified in the '@prefix'
        decorator combined with the name of the property. For example @prefix('response.config') with property
        content_type will result in a final path of response.config.content-type.

        Once a model_type has been instantiated once it will be cached and a copy of the cached
        instance will be returned on subsequent invocations.

        This method will not read the yml config file from disk each time this function is invoked.
        Rather, the yaml file will be parsed and cached when this loader is first instantiated and the cached
        parse result will be reused.

        :param model_type: The configuration class to be instantiated and populated with values pulled from the
            globally parsed yaml file.
        :return: A deep copy of the populated instance of model_type.
        """

        if model_type in self._configs:
            return copy.deepcopy(self._configs[model_type])

        configurable_properties = self._read_configurable_properties(model_type)
        model_instance = model_type()

        self._populate(model_instance, configurable_properties)
        self._try_invoke_post_construct(model_instance)

        self._configs[model_type] = model_instance

        _log.info(make_string(model_instance))

        return copy.deepcopy(model_instance)

    def _populate(self, model_instance: T, configurable_properties: Dict[str, str]):
        for name, path in configurable_properties.items():
            value = self._read_property(path)
            if value is None:
                continue
            setattr(model_instance, name, value)

    def _try_invoke_post_construct(self, model_instance: T):
        method_name = get_post_construct_name(model_instance)
        if method_name is None:
            return
        if not hasattr(model_instance, method_name):
            raise MissingPostConstructMethod(method_name, model_instance)
        getattr(model_instance, method_name)()

    def _read_property(self, property_path: str) -> Any:
        try:
            options = self._parsed_yml
            segments = property_path.split('.')
            for i in range(len(segments) - 1):
                options = options[segments[i]]
            return options[segments[-1]]
        except Exception as e:
            pass

    def _read_configurable_properties(self, model_type: Type) -> Dict[str, str]:
        prefix = get_prefix(model_type)
        properties = [prop for prop in dir(model_type) if not prop.startswith('_')]
        return {prop: f'{prefix}.{prop.replace("_", "-")}' for prop in properties}

    def _parse_config_yml(self) -> Dict | None:
        config_path = get_root_path().joinpath('_config.yml')
        if not config_path.is_file():
            _log.info('No config file found. A config file named _config.yml can be added to the root of the '
                      '.har directory to customize the app behaviour.')
            return None

        _log.info(f'Loading configuration from file: [{config_path}]')
        with open(config_path, 'r', encoding='utf-8') as file:
            content = '\n'.join(file.readlines())
        return yaml.safe_load(content)


@lru_cache()
def with_config_loader() -> ConfigLoader:
    return ConfigLoader()
