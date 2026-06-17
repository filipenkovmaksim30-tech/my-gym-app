from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import asyncio

DATABASE_URL = "postgresql+asyncpg://postgres@localhost:5432/gym_db"

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session():
    async with async_session_factory() as session:
        yield session

async def init_tables():
    from app.backend.databases.models import Base as ModelBase
    
    async with async_engine.begin() as conn:
        await conn.run_sync(ModelBase.metadata.drop_all)
        await conn.run_sync(ModelBase.metadata.create_all)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_tables())