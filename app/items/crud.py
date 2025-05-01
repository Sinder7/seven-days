from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import Item
from .schemas import ItemSchema


class ItemDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Item]:
        result = await self.session.execute(select(Item).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, item: ItemSchema) -> Item:
        db_item = Item(**item.dict())
        self.session.add(db_item)
        self.session.commit()
        self.session.refresh(db_item)
        return db_item  
