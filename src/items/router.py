from fastapi import APIRouter, Form, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from .dao import ItemDAO
from .schemas import ItemSchema
from src.database.session import get_session


router: APIRouter = APIRouter(prefix="/items", tags=["item"])
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


async def get_dao(session: AsyncSession = Depends(get_session)) -> ItemDAO:
    return ItemDAO(session=session)


@router.get(
    "/",
    response_model=list[ItemSchema],
    status_code=status.HTTP_200_OK,
    response_class=HTMLResponse,
)
async def get_all_item(dao: ItemDAO = Depends(get_dao)):
    items = await dao.get_all()
    return templates.TemplateResponse(
        request=Request, name="items/index.html", context={"items": items}
    )
