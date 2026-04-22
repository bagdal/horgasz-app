from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Halfaj
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./horgasz.db")

# Validate DATABASE_URL format
if DATABASE_URL and not DATABASE_URL.startswith(("sqlite://", "postgresql://", "mysql://", "postgresql+psycopg2://")):
    DATABASE_URL = "sqlite:///./horgasz.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Halfajok inicializálása, ha még nincsenek
    db = SessionLocal()
    try:
        if db.query(Halfaj).count() == 0:
            halfajok = [
                Halfaj(nev="Ponty", aktiv=True),
                Halfaj(nev="Amur", aktiv=True),
                Halfaj(nev="Csuka", aktiv=True),
                Halfaj(nev="Harcsa", aktiv=True),
                Halfaj(nev="Kárász", aktiv=True),
                Halfaj(nev="Dévér", aktiv=True),
                Halfaj(nev="Süllő", aktiv=True),
                Halfaj(nev="Balín", aktiv=True),
                Halfaj(nev="Compó", aktiv=True),
                Halfaj(nev="Márna", aktiv=True),
                Halfaj(nev="Domolykó", aktiv=True),
                Halfaj(nev="Gőte", aktiv=True),
                Halfaj(nev="Párna", aktiv=True),
                Halfaj(nev="Bárbo", aktiv=True),
                Halfaj(nev="Bíboros", aktiv=True),
            ]
            db.add_all(halfajok)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
