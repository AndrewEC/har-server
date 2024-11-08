from typing import Type, TypeVar, Dict, Any, Annotated
from functools import lru_cache
import logging
import copy

from pydantic import BaseModel
from fastapi import Depends

from .functions import make_debug_string
from .prefix import get_prefix, NotPrefixedException
from .post_construct import invoke_post_construct
from .parser import ConfigParser, with_config_parser


T = TypeVar('T', bound=BaseModel)
_log = logging.getLogger(__file__)


class ConfigLoader:

    def __init__(self, config_parser: ConfigParser):
        self._configs: Dict[Type, Any] = {}
        self._parsed_yml = config_parser.parse_config_yml()

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

        properties = self._read_configured_properties(model_type)
        model_instance = model_type(**properties)

        invoke_post_construct(model_instance)

        self._configs[model_type] = model_instance

        _log.info(f'Loaded config: [{make_debug_string(model_instance)}]')

        return copy.deepcopy(model_instance)

    def _read_property_from_yml(self, property_path: str) -> Any:
        try:
            options = self._parsed_yml
            segments = property_path.split('.')
            for i in range(len(segments) - 1):
                options = options[segments[i]]
            return options[segments[-1]]
        except Exception:
            pass

    def _read_configured_properties(self, model_type: Type[T]) -> Dict[str, Any]:
        prefix = get_prefix(model_type)
        if prefix is None:
            raise NotPrefixedException(model_type)

        properties = [prop for prop in model_type.model_fields if not prop.startswith('_')]
        property_values = {prop: self._read_property_from_yml(self._form_property_path(prefix, prop)) for prop in properties}
        return {name: value for name, value in property_values.items() if value is not None}

    def _form_property_path(self, prefix: str, property_name: str) -> str:
        final_property_name = property_name.replace('_', '-')
        return f'{prefix}.{final_property_name}'


@lru_cache()
def with_config_loader(parser: Annotated[ConfigParser, Depends(with_config_parser)]) -> ConfigLoader:
    return ConfigLoader(parser)
