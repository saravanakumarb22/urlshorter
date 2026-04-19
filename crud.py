from sqlalchemy.orm import Session
from models import URL
from utils import generate_short_code

def create_short_url(db: Session, original_url: str):
    code = generate_short_code()
    # Make sure code is unique
    while db.query(URL).filter(URL.short_code == code).first():
        code = generate_short_code()
    
    url_entry = URL(original_url=original_url, short_code=code)
    db.add(url_entry)
    db.commit()
    db.refresh(url_entry)
    return url_entry

def get_url_by_code(db: Session, short_code: str):
    return db.query(URL).filter(URL.short_code == short_code).first()

def increment_click(db: Session, url_entry: URL):
    url_entry.click_count += 1
    db.commit()