from pydantic import BaseModel, HttpUrl, conint, constr, condate
from typing import Optional, List
from datetime import date


class SBook(BaseModel):
    id: conint(gt=0)
    title: constr(max_length=255)
    author: constr(max_length=63)
    release_date: conint(gt=1900)
    genre: constr(max_length=63)
    pages: Optional[int] = None
    is_available: Optional[bool] = None
    cover_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    rating: Optional[float] = None
    subjects: Optional[List[str]] = None

    class Config:
        json_encoders = {
            HttpUrl: lambda v: str(v) if v else None
        }
