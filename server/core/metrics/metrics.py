from typing import Dict, List, Any, Annotated
from functools import lru_cache
from threading import Lock

from fastapi import Depends

from server.core.config import with_config_loader, ConfigLoader
from server.core.har.models import HarEntryRequest, HarEntryResponse


class Metric:

    def __init__(self, entry_id: str, response: HarEntryResponse, requests: List[HarEntryRequest]):
        self.entry_id = entry_id
        self.response = response
        self.requests = requests

    def to_dict(self) -> Dict[str, Any]:
        return {
            'entry_id': self.entry_id,
            'response': self.response.to_dict(),
            'requests': [request.to_dict() for request in self.requests]
        }


class MetricRecorder:

    def __init__(self, config_loader: ConfigLoader):
        self._recorded: List[Metric] = []
        self._lock = Lock()
        self._is_enabled = config_loader.get_app_config().debug.enable_metrics

    def record(self, entry_id: str, request: HarEntryRequest, response: HarEntryResponse):
        with self._lock:
            existing = next((metric for metric in self._recorded if metric.entry_id == entry_id), None)
            if existing:
                existing.requests.append(request)
            else:
                self._recorded.append(Metric(entry_id, response, [request]))

    def get_metrics(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [metric.to_dict() for metric in self._recorded]

    def is_enabled(self) -> bool:
        return self._is_enabled


@lru_cache()
def with_metric_recorder(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> MetricRecorder:
    return MetricRecorder(config_loader)
