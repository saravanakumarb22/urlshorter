from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class URLCreate(BaseModel):
    original_url: str

class URLResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    short_url: str | None = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True