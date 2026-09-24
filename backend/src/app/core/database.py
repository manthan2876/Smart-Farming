from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
from app.core.session import create_app_engine

engine = create_app_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()