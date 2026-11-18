from fastapi import APIRouter, status
from routers.stub_helpers import NOT_IMPLEMENTED, _not_implemented
from schema_validations import Client as ClientSchema

router = APIRouter(prefix="/api/v1/clients", tags=["clients"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

@router.get("", response_model=list[ClientSchema], responses=NOT_IMPLEMENTED)
def list_clients():
    _not_implemented()

@router.get("/{id}", response_model=ClientSchema, responses=NOT_IMPLEMENTED)
def get_client(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_client(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_client(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_client(id: int):
    _not_implemented()

@router.get("/{id}/orders", responses=NOT_IMPLEMENTED)
def list_client_orders(id: int):
    _not_implemented()
