from fastapi import APIRouter, HTTPException, Depends
from typing import Annotated, List, Dict
from app.repository.repository import BookRepository
from app.models.models import SBook
from app.core.config import ERROR_404, ERROR_500
from app.dependencies.dependencies import get_book_service
from app.services.book_service import BookService


router = APIRouter(
    prefix='/books',
    tags=['Книги']
)


@router.get(
    '',
    name='Получение всех книг',
    response_model=List[SBook],
    responses={
        200: {"description": "Список всех книг"},
        500: {"description": ERROR_500},
    }
)
async def get_books(
        repo: BookRepository = Depends()
) -> List[SBook]:
    return await repo.get_all_books()


@router.get(
    '/{book_id}',
    name='Получение книги по id',
    response_model=SBook,
    responses={
        200: {"description": "Книга полученная по id"},
        404: {"description": ERROR_404},
        500: {"description": ERROR_500},
    }
)
async def get_book_id(
    book_id: int,
    service: BookService = Depends(get_book_service)
) -> SBook:
    return await service.get_book(book_id)


@router.post(
    '',
    name='Добавление книги',
    response_model=SBook,
    responses={
        201: {"description": "Книга создана успешно"},
        400: {"description": "Book with this ID already exists"},
        500: {"description": ERROR_500},
    }
)
async def add_book(
        book: SBook,
        service: BookService = Depends(get_book_service)
) -> SBook:
    return await service.create_book(book)


@router.put(
    '/{book_id}',
    name='Внести изменения для книги',
    response_model=SBook,
    responses={
        201: {"description": "Данные успешно изменены"},
        400: {"description": "ID in path and body must match"},
        404: {"description": ERROR_404},
        500: {"description": ERROR_500},
    }
)
async def update_book_id(
        book_id: int,
        book: SBook,
        service: BookService = Depends(get_book_service)
) -> SBook:
    if book_id != book.id:
        raise HTTPException(status_code=400, detail="ID in path and body must match")
    return await service.update_book(book_id, book)


@router.delete(
    '/{book_id}',
    name='Удаление книги',
    responses={
        204: {"description": "Книга успешно удалена"},
        404: {"description": ERROR_404},
        500: {"description": ERROR_500},
    }
)
async def delete_book_id(
        book_id: int,
        service: BookService = Depends(get_book_service)
) -> Dict:
    await service.delete_book(book_id)
    return {"message": "Книга успешно удалена"}


@router.get(
    '/{book_id}/enrich',
    name='Наполнение информации о книге',
    response_model=SBook,
    responses={
        200: {"description": "Информация успешно наполнена"},
        404: {"description": ERROR_404},
        500: {"description": ERROR_500},
    }
)
async def enrich_book(
        book_id: int,
        service: BookService = Depends(get_book_service)
) -> SBook:
    return await service.enrich_book(book_id)


