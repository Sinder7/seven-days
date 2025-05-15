from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel

from .base import Base

T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: Type[T] = None

    def __init__(self, session: AsyncSession):
        self.session = session
        if self.model is None:
            raise ValueError("Модель должна быть указана в дочернем классе")

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def create(self, values: BaseModel) -> T:
        try:
            data = self.model(**values.model_dump())
            await self.session.add(data)
            await self.session.commit()
            await self.session.refresh(data)
            return data
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise ValueError(f"Ошибка при создании записи {e}")
