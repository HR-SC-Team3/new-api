from fastapi import APIRouter, status
from routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from schema_validations import ItemLine as ItemLineSchema

router = APIRouter(prefix="/api/v1/item_lines", tags=["item_lines"])
@router.get("", response_model=list[ItemLineSchema], responses=NOT_IMPLEMENTED)
def list_item_lines():
    _not_implemented()

@router.get("/{id}", response_model=ItemLineSchema, responses=NOT_IMPLEMENTED)
def get_item_line(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_item_line(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_item_line(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_item_line(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_item_line_items(id: int):
    _not_implemented()
