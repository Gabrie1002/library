import httpx
from typing import Dict, Optional, Any

from app.core.logger import logger
from app.interfaces.base_api_client import BaseApiClient


class OpenLibraryClient(BaseApiClient):
    """Взаимодействие с OpenLibrary"""
    def _get_base_url(self) -> str:
        return "https://openlibrary.org"

    def _get_headers(self) -> Dict[str, str]:
        return {}

    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
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


class OpenLibraryService:

    """Наполнение книг с API OpenLibrary"""

    def __init__(self, client: OpenLibraryClient):
        self._client = client

    async def search_book(self, title: str, author: str) -> Optional[Dict]:
        try:
            data = await self._client._make_request(
                "GET",
                "/search.json",
                params={"title": title, "author": author, "limit": 1}
            )
            return data.get("docs", [None])[0]
        except Exception as e:
            logger.error(f"OpenLibrary API error: {e}")
            return None

    async def get_book_details(self, olid: str) -> Optional[Dict]:
        try:
            return await self._client._make_request("GET", f"/works/{olid}.json")
        except Exception as e:
            logger.error(f"OpenLibrary details error: {e}")
            return None

    async def enrich_book_data(self, title: str, author: str) -> Dict:
        search_result = await self.search_book(title, author)
        if not search_result:
            return {}

        olid = search_result.get("cover_edition_key")
        details = await self.get_book_details(search_result["key"]) if "key" in search_result else None

        return {
            "cover_url": f"https://covers.openlibrary.org/b/olid/{olid}-L.jpg" if olid else None,
            "description": self._extract_description(details),
            "rating": search_result.get("ratings_average"),
            "publish_date": search_result.get("first_publish_year"),
            "subjects": search_result.get("subject", [])[:3]
        }

    @staticmethod
    def _extract_description(details: Optional[Dict]) -> Optional[str]:
        if not details:
            return None
        description = details.get("description")
        if isinstance(description, dict):
            return description.get("value")
        return description
