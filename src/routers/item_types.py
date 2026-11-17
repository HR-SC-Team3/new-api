from fastapi import APIRouter, status
from src.routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from src.schema_validations import ItemType as ItemTypeSchema

router = APIRouter(prefix="/api/v1/item_types", tags=["item_types"])

@router.get("", response_model=list[ItemTypeSchema], responses=NOT_IMPLEMENTED)
def list_item_types():
    _not_implemented()

@router.get("/{id}", response_model=ItemTypeSchema, responses=NOT_IMPLEMENTED)
def get_item_type(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_item_type(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_item_type(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_item_type(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_item_type_items(id: int):
    _not_implemented()
