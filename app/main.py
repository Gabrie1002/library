from fastapi import FastAPI
from app.routers.routers import router as book_router


app = FastAPI()

app.include_router(book_router)


