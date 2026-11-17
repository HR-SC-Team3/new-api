from fastapi import APIRouter, status
from src.routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from src.schema_validations import Order as OrderSchema

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

@router.get("", response_model=list[OrderSchema], responses=NOT_IMPLEMENTED)
def list_orders():
    _not_implemented()

@router.get("/{id}", response_model=OrderSchema, responses=NOT_IMPLEMENTED)
def get_order(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_order(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_order(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_order(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_order_items(id: int):
    _not_implemented()

@router.put("/{id}/items", responses=NOT_IMPLEMENTED)
def replace_order_items(id: int, data: list[dict]):
    _not_implemented()
