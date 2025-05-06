from app.repository.repository import BookRepository
from fastapi import Depends
from app.services.book_service import BookService


async def get_repository():
    return BookRepository()


def get_book_service(repo: BookRepository = Depends()) -> BookService:
    return BookService(repo)

