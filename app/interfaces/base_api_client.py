from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseApiClient(ABC):
    """Абстрактная функция для взаимодействия с другими API"""
    @abstractmethod
    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        pass

    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        pass

