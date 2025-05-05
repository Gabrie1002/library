from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, List, Dict
from src.library_catalog.repository import BookRepository
from src.library_catalog.models import SBook

router = APIRouter(
    prefix='/books',
    tags=['Книги']
)


@router.get('', name='Получение всех книг')
async def get_books(
        repo: BookRepository = Depends()
) -> List[SBook]:
    return await repo.get_all_books()


@router.get('/{book_id}', name='Получение книги по id')
async def get_book_id(
        book_id: int, repo: BookRepository = Depends()
) -> SBook:
    book = await repo.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post('', name='Добавление книги')
async def add_book(
        book: Annotated[SBook, Depends()],
        repo: BookRepository = Depends()
) -> SBook:
    existing_book = await repo.get_book(book.id)
    if existing_book:
        raise HTTPException(status_code=400, detail="Book with this ID already exists")
    return await repo.add_book(book)


@router.put('/{book_id}', name='Внести изменения для книги')
async def update_book_id(
        book_id: int,
        book: Annotated[SBook, Depends()],
        repo: BookRepository = Depends()
) -> SBook:
    if book_id != book.id:
        raise HTTPException(status_code=400, detail="ID in path and body must match")
    updated_book = await repo.update_book(book_id, book)
    if not updated_book:
        raise HTTPException(status_code=404, detail="Book not found")
    return updated_book


@router.delete('/{book_id}', name='Удаление книги')
async def delete_book_id(
        book_id: int,
        repo: BookRepository = Depends()
) -> Dict:
    success = await repo.delete_book(book_id)
    if not success:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}


@router.post("/books/{book_id}/enrich")
async def enrich_book(
        book_id: int,
        repo: BookRepository = Depends()
) -> SBook:
    book = await repo.get_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    enriched_data = await repo.open_library.enrich_book_data(
        title=book.title,
        author=book.author
    )

    updated_book = await repo.update_book(
        book_id,
        {**book.dict(), **enriched_data}
    )
    return updated_book

