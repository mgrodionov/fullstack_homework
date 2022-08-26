from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=False, future=True)

Base = declarative_base()
