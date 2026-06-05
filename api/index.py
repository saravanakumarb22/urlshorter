# from fastapi import FastAPI, Depends, HTTPException, Form, Request
# from fastapi.responses import RedirectResponse, HTMLResponse
# from sqlalchemy.orm import Session
# from database import engine, get_db
# import models, crud, schemas
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# from typing import List

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI()


# @app.get("/")
# def serve_frontend():
#     return FileResponse("index.html")

# # Shorten a URL (supports form input)
# @app.post("/shorten", response_model=schemas.URLResponse)
# def shorten_url(original_url: str = Form(...), db: Session = Depends(get_db), request: Request = None):
#     url_entry = crud.create_short_url(db, original_url)
#     # attach full URL to response
#     url_entry.short_url = f"{request.base_url}{url_entry.short_code}"
#     return url_entry

# # Redirect to original URL
# @app.get("/{short_code}")
# def redirect_url(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     crud.increment_click(db, url_entry)
#     return RedirectResponse(url=url_entry.original_url)

# # Get stats
# @app.get("/stats/{short_code}", response_model=schemas.URLResponse)
# def get_stats(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     return url_entry


# @app.get("/links", response_model=List[schemas.URLResponse])
# def get_all_links(db: Session = Depends(get_db)):
#     return db.query(models.URL).order_by(models.URL.created_at.desc()).all()

# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.responses import RedirectResponse, FileResponse
# from sqlalchemy.orm import Session
# from database import engine, get_db
# from typing import List
# import models, crud, schemas

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # ── Frontend ──────────────────────────────────────
# @app.get("/")
# def serve_frontend():
#     return FileResponse("index.html")

# # ── Shorten  (JSON body, not Form) ───────────────
# @app.post("/shorten", response_model=schemas.URLResponse)
# def shorten_url(data: schemas.URLCreate, db: Session = Depends(get_db)):
#     return crud.create_short_url(db, data.original_url)

# # ── All links  (must be before /{short_code}) ────
# @app.get("/links", response_model=List[schemas.URLResponse])
# def get_all_links(db: Session = Depends(get_db)):
#     return db.query(models.URL).order_by(models.URL.created_at.desc()).all()

# # ── Stats  (must be before /{short_code}) ────────
# @app.get("/stats/{short_code}", response_model=schemas.URLResponse)
# def get_stats(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     return url_entry

# # ── Redirect  (must be LAST — catches everything) ─
# @app.get("/{short_code}")
# def redirect_url(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     crud.increment_click(db, url_entry)
#     return RedirectResponse(url=url_entry.original_url)

# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.responses import RedirectResponse, FileResponse
# from fastapi.middleware.cors import CORSMiddleware          # ← add this
# from sqlalchemy.orm import Session
# from database import engine, get_db
# from typing import List
# import models, crud, schemas

# models.Base.metadata.create_all(bind=engine)

# app = FastAPI()

# # ── CORS  (add this block right after app = FastAPI()) ──
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ── Frontend ──────────────────────────────────────
# @app.get("/")
# def serve_frontend():
#     return FileResponse("index.html")

# # ── Shorten ───────────────────────────────────────
# @app.post("/shorten", response_model=schemas.URLResponse)
# def shorten_url(data: schemas.URLCreate, db: Session = Depends(get_db)):
#     return crud.create_short_url(db, data.original_url)

# # ── All links  (before /{short_code}) ────────────
# @app.get("/links", response_model=List[schemas.URLResponse])
# def get_all_links(db: Session = Depends(get_db)):
#     return db.query(models.URL).order_by(models.URL.created_at.desc()).all()

# # ── Stats  (before /{short_code}) ─────────────────
# @app.get("/stats/{short_code}", response_model=schemas.URLResponse)
# def get_stats(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     return url_entry

# # ── Redirect  (last — catches everything) ─────────
# @app.get("/{short_code}")
# def redirect_url(short_code: str, db: Session = Depends(get_db)):
#     url_entry = crud.get_url_by_code(db, short_code)
#     if not url_entry:
#         raise HTTPException(status_code=404, detail="URL not found")
#     crud.increment_click(db, url_entry)
#     return RedirectResponse(url=url_entry.original_url)


from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import os, random, string
from dotenv import load_dotenv

load_dotenv()

# ── Database ──────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
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

# ── Utils ─────────────────────────────────────────
def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ── DB helpers ────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

# Read index.html once
import pathlib
HTML_FILE = pathlib.Path(__file__).parent.parent / "index.html"

@app.get("/")
def serve_frontend():
    return HTMLResponse(HTML_FILE.read_text())

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