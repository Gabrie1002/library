from pydantic import BaseModel, HttpUrl
from typing import Optional, List


class SBook(BaseModel):
    id: int
    title: str
    author: str
    release_date: int
    genre: str
    pages: Optional[int] = None
    is_available: bool
    cover_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    subjects: Optional[List[str]] = None

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v) if v else None
        }
