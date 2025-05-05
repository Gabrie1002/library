from fastapi import FastAPI
import json
import os
from src.library_catalog.routers import router as book_router
from src.library_catalog.database import JSON_FILE

if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

app = FastAPI()

app.include_router(book_router)


