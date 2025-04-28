from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)


from config import config

async_engine: AsyncEngine = create_async_engine(url=config.db_url, echo=config.db_echo)
async_session = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
