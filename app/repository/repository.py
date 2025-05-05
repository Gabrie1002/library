from dotenv import load_dotenv
from typing import Dict, Optional, List, Tuple, Union
import json
from app.models.models import SBook
from app.core.logger import log_exceptions
from app.services.book_service import OpenLibraryService, OpenLibraryClient
from app.services.jsonbin_service import JsonBinClient
load_dotenv()


class BookRepository:
    """Работа с моделью Book"""
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


