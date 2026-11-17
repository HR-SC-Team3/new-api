from fastapi import APIRouter, status
from src.routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from src.schema_validations import Supplier as SupplierSchema

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])

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
