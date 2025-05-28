# main.py
from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
import uuid
from datetime import datetime

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Настройки
DATA_FILE = "store_data.json"
SALES_FILE = "sales_data.json"
ITEMS_PER_PAGE = 5


# Модель данных
class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    created_at: str
    updated_at: str


class Sale(BaseModel):
    id: str
    item_id: str
    item_name: str
    quantity_sold: int
    sale_price: float
    sale_date: str


# Инициализация данных
def load_data() -> Dict[str, Item]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            return {item["id"]: Item(**item) for item in data}
    return {}


def load_sales() -> Dict[str, Sale]:
    if os.path.exists(SALES_FILE):
        with open(SALES_FILE, "r") as f:
            data = json.load(f)
            return {sale["id"]: Sale(**sale) for sale in data}
    return {}


def save_data(items: Dict[str, Item]):
    data = [item.dict() for item in items.values()]
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_sales(sales: Dict[str, Sale]):
    data = [sale.dict() for sale in sales.values()]
    with open(SALES_FILE, "w") as f:
        json.dump(data, f, indent=2)


# Инициализация данных при запуске
store_items = load_data()
store_sales = load_sales()


# Аутентификация (для демонстрации)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "securepassword"


# Утилиты
def is_authenticated(request: Request) -> bool:
    return request.cookies.get("session") == "authenticated"


def get_current_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Роуты
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "home.html", {"request": request, "is_authenticated": is_authenticated(request)}
    )


@app.get("/items", response_class=HTMLResponse)
async def list_items(request: Request, page: int = 1, search: Optional[str] = None):
    # Фильтрация и поиск
    filtered_items = list(store_items.values())

    if search:
        search = search.lower()
        filtered_items = [
            item
            for item in filtered_items
            if search in item.name.lower()
            or (item.description and search in item.description.lower())
        ]

    # Пагинация
    total_items = len(filtered_items)
    total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = min(start_index + ITEMS_PER_PAGE, total_items)
    page_items = filtered_items[start_index:end_index]

    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": page_items,
            "page": page,
            "total_pages": total_pages,
            "search_query": search or "",
            "is_authenticated": is_authenticated(request),
            "total_items": total_items,
        },
    )


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request, error: Optional[str] = None):
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": error}
    )


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        response = RedirectResponse(url="/items", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="session", value="authenticated")
        return response

    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Invalid credentials"}
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("session")
    return response


@app.get("/add-item", response_class=HTMLResponse)
async def add_item_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("add_item.html", {"request": request})


@app.post("/add-item", response_class=HTMLResponse)
async def create_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    item_id = str(uuid.uuid4())
    current_time = get_current_datetime()

    new_item = Item(
        id=item_id,
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        created_at=current_time,
        updated_at=current_time,
    )

    store_items[item_id] = new_item
    save_data(store_items)

    return RedirectResponse(url=f"/item/{item_id}", status_code=303)


@app.get("/new-sale", response_class=HTMLResponse)
async def new_sale_form(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "new_sale.html", {"request": request, "items": store_items.values()}
    )


@app.post("/new-sale", response_class=HTMLResponse)
async def create_sale(
    request: Request, item_id: str = Form(...), quantity_sold: int = Form(...)
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    item = store_items.get(item_id)
    if not item:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Item not found"}
        )

    if item.quantity < quantity_sold:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "message": f"Not enough stock. Only {item.quantity} available",
            },
        )

    # Обновляем количество товара
    updated_item = Item(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity - quantity_sold,
        created_at=item.created_at,
        updated_at=get_current_datetime(),
    )
    store_items[item_id] = updated_item
    save_data(store_items)

    # Создаем запись о продаже
    sale_id = str(uuid.uuid4())
    new_sale = Sale(
        id=sale_id,
        item_id=item_id,
        item_name=item.name,
        quantity_sold=quantity_sold,
        sale_price=item.price * quantity_sold,
        sale_date=get_current_datetime(),
    )
    store_sales[sale_id] = new_sale
    save_sales(store_sales)

    return RedirectResponse(url=f"/sale/{sale_id}", status_code=303)


@app.get("/sale/{sale_id}", response_class=HTMLResponse)
async def sale_detail(request: Request, sale_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    sale = store_sales.get(sale_id)
    if not sale:
        return templates.TemplateResponse(
            "error.html", {"request": request, "message": "Sale not found"}
        )

    return templates.TemplateResponse(
        "sale_detail.html", {"request": request, "sale": sale}
    )


@app.get("/sales", response_class=HTMLResponse)
async def sales_list(request: Request, date: Optional[str] = None, page: int = 1):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    # Фильтрация по дате
    filtered_sales = list(store_sales.values())
    if date:
        filtered_sales = [s for s in filtered_sales if s.sale_date.startswith(date)]

    # Пагинация
    total_sales = len(filtered_sales)
    total_pages = (total_sales + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = min(start_index + ITEMS_PER_PAGE, total_sales)
    page_sales = filtered_sales[start_index:end_index]

    return templates.TemplateResponse(
        "sales.html",
        {
            "request": request,
            "sales": page_sales,
            "page": page,
            "total_pages": total_pages,
            "date_filter": date or "",
            "total_sales": total_sales,
        },
    )


@app.get("/statistics", response_class=HTMLResponse)
async def statistics(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    # Расчет статистики
    today = datetime.now().strftime("%Y-%m-%d")
    this_month = datetime.now().strftime("%Y-%m")

    # Статистика за день
    daily_sales = [s for s in store_sales.values() if s.sale_date.startswith(today)]
    daily_revenue = sum(s.sale_price for s in daily_sales)
    daily_items_sold = sum(s.quantity_sold for s in daily_sales)

    # Статистика за месяц
    monthly_sales = [
        s for s in store_sales.values() if s.sale_date.startswith(this_month)
    ]
    monthly_revenue = sum(s.sale_price for s in monthly_sales)
    monthly_items_sold = sum(s.quantity_sold for s in monthly_sales)

    # Топ продаваемых товаров
    item_sales = {}
    for sale in store_sales.values():
        if sale.item_id not in item_sales:
            item_sales[sale.item_id] = {
                "name": sale.item_name,
                "quantity": 0,
                "revenue": 0,
            }
        item_sales[sale.item_id]["quantity"] += sale.quantity_sold
        item_sales[sale.item_id]["revenue"] += sale.sale_price

    top_items = sorted(item_sales.values(), key=lambda x: x["quantity"], reverse=True)[
        :5
    ]

    return templates.TemplateResponse(
        "statistics.html",
        {
            "request": request,
            "daily_revenue": daily_revenue,
            "daily_items_sold": daily_items_sold,
            "monthly_revenue": monthly_revenue,
            "monthly_items_sold": monthly_items_sold,
            "top_items": top_items,
            "today": today,
            "this_month": this_month,
        },
    )


@app.get("/item/{item_id}", response_class=HTMLResponse)
async def item_detail(request: Request, item_id: str):
    item = store_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return templates.TemplateResponse(
        "item_detail.html",
        {
            "request": request,
            "item": item,
            "is_authenticated": is_authenticated(request),
        },
    )


@app.get("/edit-item/{item_id}", response_class=HTMLResponse)
async def edit_item_form(request: Request, item_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    item = store_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return templates.TemplateResponse(
        "edit_item.html", {"request": request, "item": item}
    )


@app.post("/edit-item/{item_id}", response_class=HTMLResponse)
async def update_item(
    request: Request,
    item_id: str,
    name: str = Form(...),
    description: str = Form(""),
    price: float = Form(...),
    quantity: int = Form(...),
):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    item = store_items.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    updated_item = Item(
        id=item_id,
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        created_at=item.created_at,
        updated_at=get_current_datetime(),
    )

    store_items[item_id] = updated_item
    save_data(store_items)

    return RedirectResponse(url=f"/item/{item_id}", status_code=303)


@app.get("/delete-item/{item_id}", response_class=HTMLResponse)
async def delete_item(request: Request, item_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/login")

    if item_id in store_items:
        del store_items[item_id]
        save_data(store_items)

    return RedirectResponse(url="/items", status_code=303)


@app.get("/low-stock", response_class=HTMLResponse)
async def low_stock_items(request: Request):
    low_stock = [item for item in store_items.values() if item.quantity < 5]

    return templates.TemplateResponse(
        "low_stock.html",
        {
            "request": request,
            "items": low_stock,
            "is_authenticated": is_authenticated(request),
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
