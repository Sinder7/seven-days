from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession

from .dao import ItemDAO
from .schemas import ItemSchema
from app.database.session import get_session


router: APIRouter = APIRouter(prefix="/items", tags=["item"])


async def get_dao(session: AsyncSession = Depends(get_session)) -> ItemDAO:
    return ItemDAO(session=session)


@router.get("/", response_model=list[ItemSchema])
async def get_all_item(dao: ItemDAO = Depends(get_dao)):
    items = await dao.get_all()
    return items

