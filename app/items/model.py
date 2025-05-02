from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Float

from database.base import Base


class Item(Base):
    __tablename__ = "items"

    name: Mapped[str] = mapped_column(String(50))
    articule: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer, default=0)

    def ___repr__(self) -> str:
        return f"Item(id={self.id!r}), name={self.name!r}"


print(type(Item))