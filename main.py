import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.items.router import router as item_router

logging.basicConfig(
    level=logging.INFO,
    filename="app_log.log",
    filemode="a",
    encoding="utf-8",
    format="%(asctime)s %(levelname)s %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logging.info("Инициализация приложения...  ")
    yield
    logging.info("Завершение работы приложения...")


def create_app() -> FastAPI:

    app: FastAPI = FastAPI(title="seven-day-app", version="0.1.0", lifespan=lifespan)

    app.include_router(item_router)

    return app


app = create_app()
