from fastapi import APIRouter, HTTPException, status

from src.schema_validations import ItemGroup as ItemGroupSchema

router = APIRouter(prefix="/api/v1/item_groups", tags=["item_groups"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[ItemGroupSchema], responses=NOT_IMPLEMENTED)
def list_item_groups():
    _not_implemented()

@router.get("/{id}", response_model=ItemGroupSchema, responses=NOT_IMPLEMENTED)
def get_item_group(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_item_group(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_item_group(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_item_group(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_item_group_items(id: int):
    _not_implemented()
