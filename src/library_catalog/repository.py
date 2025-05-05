from abc import ABC, abstractmethod
import httpx
import os
from dotenv import load_dotenv
from typing import Dict, Optional, List, Tuple, Any, Union
import json
from src.library_catalog.models import SBook
from src.library_catalog.logger import log_exceptions, logger

load_dotenv()


class BaseApiClient(ABC):
    @abstractmethod
    async def _make_request(self, method: str, url: str, **kwargs) -> Any:
        pass

    @abstractmethod
    def _get_base_url(self) -> str:
        pass

    @abstractmethod
    def _get_headers(self) -> Dict[str, str]:
        pass


class JsonBinClient(BaseApiClient):
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


class OpenLibraryClient(BaseApiClient):
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


class BookRepository:
    def __init__(self):
        self._client = JsonBinClient()
        self.open_library = OpenLibraryService(OpenLibraryClient())

    @log_exceptions
    async def get_all_books(self) -> List[SBook]:
        response = await self._client._make_request("GET")
        books_data = response.get("record", [])

        if isinstance(books_data, dict):
            if "record" in books_data:
                books_data = books_data["record"]
            elif "id" in books_data:
                books_data = [books_data]

        return [SBook(**book) for book in books_data if isinstance(book, dict)]

    @log_exceptions
    async def save_all_books(self, books: List[SBook]) -> bool:
        books_data = [json.loads(book.json()) for book in books]
        await self._client._make_request("PUT", json=books_data)
        return True

    @log_exceptions
    async def get_book(self, book_id: int) -> Optional[SBook]:
        books = await self.get_all_books()
        for book in books:
            if isinstance(book, SBook) and book.id == book_id:
                return book
        return None

    @log_exceptions
    async def add_book(self, book: SBook) -> SBook:
        book_data = book.dict()
        if book_data.get("enrich_data", True):
            enriched_data = await self.open_library.enrich_book_data(
                title=book.title,
                author=book.author
            )
            book = book.copy(update=enriched_data)
        books = await self.get_all_books()
        books.append(book)
        await self.save_all_books(books)
        return book

    @log_exceptions
    async def update_book(self, book_id: int, updated_data: Union[Dict, SBook]) -> Optional[SBook]:
        books = await self.get_all_books()

        if isinstance(updated_data, SBook):
            updated_data = updated_data.dict(exclude_unset=True)

        for i, book in enumerate(books):
            if book.id == book_id:
                updated_book = book.copy(update=updated_data)
                books[i] = updated_book
                await self.save_all_books(books)
                return updated_book
        return None

    @log_exceptions
    async def delete_book(self, book_id: int) -> Tuple[bool, int]:
        books = await self.get_all_books()
        initial_count = len(books)
        books = [book for book in books if book.id != book_id]

        if len(books) < initial_count:
            success = await self.save_all_books(books)
            return success, len(books)
        return False, initial_count


class OpenLibraryService:
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