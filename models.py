from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime
from database import Base

class URL(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)