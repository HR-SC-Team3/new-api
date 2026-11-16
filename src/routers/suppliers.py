from fastapi import APIRouter, HTTPException, status

from src.schema_validations import Supplier as SupplierSchema

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[SupplierSchema], responses=NOT_IMPLEMENTED)
def list_suppliers():
    _not_implemented()

@router.get("/{id}", response_model=SupplierSchema, responses=NOT_IMPLEMENTED)
def get_supplier(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_supplier(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_supplier(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_supplier(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_supplier_items(id: int):
    _not_implemented()
