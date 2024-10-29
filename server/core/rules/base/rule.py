from abc import ABC, abstractmethod

from server.core.config import ConfigLoader


class Rule(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def initialize(self, config_loader: ConfigLoader):
        pass
