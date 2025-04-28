from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine,
)


async_engine: AsyncEngine = create_async_engine(url=..., echo=...)
async_session = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
