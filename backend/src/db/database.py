from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.declarative import declarative_base
from src.core.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(url=get_settings().SQLALCHEMY_DATABASE_URL)

class Base(DeclarativeBase):
    pass

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    #async with engine.begin() as conn:
    #    await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()