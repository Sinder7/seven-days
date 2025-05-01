from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession

from .crud import ItemDAO
from schemas import ItemSchema
from database.session import get_session


router: APIRouter = APIRouter(prefix="/items", tags=["item"])


async def get_dao(session: AsyncSession = Depends(get_session)) -> ItemDAO:
    return ItemDAO(session=session)
