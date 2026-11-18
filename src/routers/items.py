from fastapi import APIRouter, HTTPException, status
from schema_validations import Item as ItemSchema, ItemInput
from schema_validations import (Inventory as InventorySchema,)

router = APIRouter(prefix="/api/v1/items", tags = ["items"])
not_implemented = {"501": {"description": "Not implemented"}}

@router.get("", response_model=list[ItemSchema], responses=not_implemented)
def list_items():
    raise HTTPException(status_code= 501, detail = "Not Implemented")

@router.get("/{id}", response_model=ItemSchema, responses=not_implemented)
def get_items(id: int):
    raise HTTPException(status_code= 501, detail = "Not Implemented")

@router.post("", status_code=status.HTTP_201_CREATED, responses=not_implemented)
def create_items(data: ItemInput):
    raise HTTPException(status_code= 501, detail = "Not Implemented")

@router.put("/{id}", responses=not_implemented)
def save_items(id: int, data: ItemInput):
    raise HTTPException(status_code= 501, detail = "Not Implemented")

@router.delete("/{id}", responses=not_implemented)
def delete_items(id: int):
    raise HTTPException(status_code= 501, detail = "Not Implemented")

@router.get("/{id}/inventory", response_model=list[InventorySchema], tags=["inventories"], responses=not_implemented,)
def get_item_inventory(id: int):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("/{id}/inventory/totals", tags=["inventories"], responses=not_implemented,)
def get_item_inventory_totals(id: int):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)
