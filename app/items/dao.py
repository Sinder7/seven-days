from database.base_dao import BaseDAO
from model import Item


class ItemDao(BaseDAO):
    model = Item
