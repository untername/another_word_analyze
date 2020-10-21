from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./analyzing_app.db"

Engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

LocalSession = sessionmaker(bind=Engine, autocommit=False, autoflush=False)

DataBase = declarative_base()


def get_db():
    db = None
    try:
        db = LocalSession()
        return db
    finally:
        db.close()
