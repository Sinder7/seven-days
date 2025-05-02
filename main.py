from fastapi import FastAPI

from app.items.router import router as item_router


app: FastAPI = FastAPI(title="seven-day-app", version="0.1.0")
app.include_router(item_router)

