from fastapi import APIRouter, HTTPException, status

from src.schema_validations import Location as LocationSchema

router = APIRouter(prefix="/api/v1/locations", tags=["locations"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[LocationSchema], responses=NOT_IMPLEMENTED)
def list_locations():
    _not_implemented()

@router.get("/{id}", response_model=LocationSchema, responses=NOT_IMPLEMENTED)
def get_location(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_location(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_location(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_location(id: int):
    _not_implemented()