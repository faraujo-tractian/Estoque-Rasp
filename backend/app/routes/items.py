"""
Items Routes
Endpoints for item management
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.services.database import Database
from app.services.google_sheets import GoogleSheetsService
from app.models.item import Item

router = APIRouter()
db = Database()


@router.get("/items", response_model=List[Item])
async def get_all_items():
    """Get all items"""
    try:
        items = db.get_all_items()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    """Get item by ID"""
    item = db.get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.get("/items/search", response_model=List[Item])
async def search_items(q: str = Query(..., min_length=2)):
    """Search items by name"""
    try:
        items = db.search_items(q)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
async def sync_with_sheets():
    """Manually trigger sync with Google Sheets"""
    try:
        sheets_service = GoogleSheetsService()
        result = await sheets_service.sync_from_sheets()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao sincronizar com Google Sheets: {str(e)}"
        )

