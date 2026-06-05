from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os, random, string, pathlib
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, connect_args={"sslmode": "require"})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ── Model ─────────────────────────────────────────
class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, nullable=False)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ── Schemas ───────────────────────────────────────
class URLCreate(BaseModel):
    original_url: str

class URLResponse(BaseModel):
    short_code: str
    original_url: str
    click_count: int
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

# ── Helpers ───────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_short_url(db: Session, original_url: str):
    code = generate_short_code()
    while db.query(URL).filter(URL.short_code == code).first():
        code = generate_short_code()
    entry = URL(original_url=original_url, short_code=code)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

# ── App ───────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html from project root
HTML_PATH = pathlib.Path(__file__).parent.parent / "index.html"

@app.get("/")
def serve_frontend():
    return HTMLResponse(HTML_PATH.read_text(encoding="utf-8"))

@app.post("/shorten", response_model=URLResponse)
def shorten_url(data: URLCreate, db: Session = Depends(get_db)):
    return create_short_url(db, data.original_url)

@app.get("/links", response_model=List[URLResponse])
def get_all_links(db: Session = Depends(get_db)):
    return db.query(URL).order_by(URL.created_at.desc()).all()

@app.get("/stats/{short_code}", response_model=URLResponse)
def get_stats(short_code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="URL not found")
    return entry

@app.get("/{short_code}")
def redirect_url(short_code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="URL not found")
    entry.click_count += 1
    db.commit()
    return RedirectResponse(url=entry.original_url)