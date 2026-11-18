from fastapi import APIRouter, HTTPException, status
from routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from schema_validations import Inventory as InventorySchema

router = APIRouter(prefix="/api/v1/inventories", tags=["inventories"])
@router.get("", response_model=list[InventorySchema], responses=NOT_IMPLEMENTED)
def list_inventories():
    _not_implemented()

@router.get("/{id}", status_code=status.HTTP_404_NOT_FOUND)
def get_inventory(id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found",)

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_inventory(data: dict):
    _not_implemented()

@router.put("/{id}", status_code=status.HTTP_404_NOT_FOUND)
def update_inventory(id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found",)

@router.delete("/{id}", status_code=status.HTTP_404_NOT_FOUND)
def delete_inventory(id: int):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found",)
