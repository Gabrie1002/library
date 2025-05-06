from fastapi import HTTPException, status


class BookNotFoundError(HTTPException):
    def __init__(self):
        detail = "Book not found."
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


ERROR_404 = "Book not found"

ERROR_500 = "Ошибка сервера"





