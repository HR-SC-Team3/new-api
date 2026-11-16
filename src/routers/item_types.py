from fastapi import APIRouter, HTTPException, status

from src.schema_validations import ItemType as ItemTypeSchema

router = APIRouter(prefix="/api/v1/item_types", tags=["item_types"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

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
