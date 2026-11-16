from fastapi import APIRouter, HTTPException, status

from src.schema_validations import Warehouse as WarehouseSchema

router = APIRouter(prefix="/api/v1/warehouses", tags=["warehouses"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[WarehouseSchema], responses=NOT_IMPLEMENTED)
def list_warehouses():
    _not_implemented()

@router.get("/{id}", response_model=WarehouseSchema, responses=NOT_IMPLEMENTED)
def get_warehouse(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_warehouse(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_warehouse(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_warehouse(id: int):
    _not_implemented()

@router.get("/{id}/locations", responses=NOT_IMPLEMENTED)
def list_warehouse_locations(id: int):
    _not_implemented()
