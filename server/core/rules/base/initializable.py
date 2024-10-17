from abc import abstractmethod, ABC

from server.core.config import ConfigLoader


class Initializeable(ABC):

    @abstractmethod
    def load_config(self, config_loader: ConfigLoader):
        pass
