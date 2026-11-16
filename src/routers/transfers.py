from fastapi import APIRouter, HTTPException, status

from src.schema_validations import Transfer as TransferSchema

router = APIRouter(prefix="/api/v1/transfers", tags=["transfers"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[TransferSchema], responses=NOT_IMPLEMENTED)
def list_transfers():
    _not_implemented()

@router.get("/{id}", response_model=TransferSchema, responses=NOT_IMPLEMENTED)
def get_transfers(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_transfers(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_transfers(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_transfers(id: int):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_transfer_items(id: int):
    _not_implemented()

@router.put("/{id}/commit", responses=NOT_IMPLEMENTED)
def commit_transfer(id: int):
    _not_implemented()