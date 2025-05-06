from app.models.models import SBook
from app.repository.repository import BookRepository
from app.core.config import BookNotFoundError


class BookService:
    def __init__(self, repo: BookRepository):
        self.repo = repo

    async def get_book(self, book_id: int) -> SBook:
        book = await self.repo.get_book(book_id)
        if not book:
            raise BookNotFoundError()
        return book

    async def create_book(self, data: SBook) -> SBook:
        return await self.repo.add_book(data)

    async def update_book(self, book_id: int, data: SBook) -> SBook:
        book = await self.repo.get_book(book_id)
        if not book:
            raise BookNotFoundError()
        return await self.repo.update_book(book_id, data)

    async def delete_book(self, book_id: int) -> None:
        book = await self.repo.get_book(book_id)
        if not book:
            raise BookNotFoundError()
        await self.repo.delete_book(book_id)

    async def get_all_books(self) -> list[SBook]:
        return await self.repo.get_all_books()

    async def enrich_book(self, book_id: int) -> SBook:
        book = await self.repo.get_book(book_id)
        if not book:
            raise BookNotFoundError()
        enriched_data = await self.repo.open_library.enrich_book_data(book.title, book.author)
        book_data = book.model_dump()
        book_data.update(enriched_data)
        return SBook(**book_data)


