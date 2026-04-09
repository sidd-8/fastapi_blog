from fastapi import FastAPI, Request, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import signal

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

items: list[dict] = [
    {"id": 1, "name": "Ice Cream", "description": "This is Ice Cream", "inventory": 10, "type": "food", "price": 5.99},
    {"id": 2, "name": "Lays", "description": "Lays are the best chips in the world", "inventory": 5, "type": "food", "price": 2.99},
    {"id": 3, "name": "Pencils", "description": "These are Pencils", "inventory": 20, "type": "stationery", "price": 0.99},
]

@app.get("/", include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"items": items, "title": "Home"})

@app.get("/api/items")
def get_items():
    return items

@app.get("/items/{item_id}", include_in_schema=False)
def get_item(request: Request, item_id: int):
    for item in items:
        if item["id"] == item_id:
            return templates.TemplateResponse(request, "items.html", {"item": item, "title": item["name"]})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

## Edge case: Should be before @app.get("/api/items/{item_id}") otherwise it will get misinterpreted as a request for an item with id "search".
@app.get("/api/items/search")
def search_items(q: str):
    result = []
    for item in items:
        if q.lower() in item["name"].lower():
            result.append(item)
    return result

## Might be better to use /api/items/id/{item_id} to avoid conflict with /api/items/search. No ambiguity in the path.
@app.get("/api/items/{item_id}")
def get_items_by_id(item_id: int):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

@app.post("/api/items")
def create_item(item: dict):
    item["id"] = len(items) + 1
    items.append(item)
    return item