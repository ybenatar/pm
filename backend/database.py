import os
from pathlib import Path
from sqlmodel import create_engine, Session, SQLModel

DB_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/pm.db")

# Ensure the parent directory exists if using local SQLite file
if DB_URL.startswith("sqlite:///"):
    db_path = DB_URL.replace("sqlite:///", "")
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if "sqlite" in DB_URL else {}
engine = create_engine(DB_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)
