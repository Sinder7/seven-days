from src.database.base_dao import BaseDAO
from .model import Item


class ItemDAO(BaseDAO):
    model = Item
