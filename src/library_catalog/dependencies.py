from src.library_catalog.repository import BookRepository


async def get_repository():
    return BookRepository()

