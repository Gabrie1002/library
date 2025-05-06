import httpx
import os
from typing import Dict, Any
from app.interfaces.base_api_client import BaseApiClient


class JsonBinClient(BaseApiClient):
    """Взаимодействие с JsonBin"""
    def __init__(self):
        self._bin_id = os.getenv("JSONBIN_BIN_ID")
        self._api_key = os.getenv("JSONBIN_API_KEY")

    def _get_base_url(self) -> str:
        return f"https://api.jsonbin.io/v3/b/{self._bin_id}"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "X-Master-Key": self._api_key,
            "Content-Type": "application/json"
        }

    async def _make_request(self, method: str, url: str = "", **kwargs) -> Any:
        async with httpx.AsyncClient() as client:
            full_url = f"{self._get_base_url()}{url}"
            response = await client.request(
                method,
                full_url,
                headers=self._get_headers(),
                **kwargs
            )
            response.raise_for_status()
            return response.json()
