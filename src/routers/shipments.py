from fastapi import APIRouter, HTTPException, status

from src.schema_validations import Shipment as ShipmentSchema

router = APIRouter(prefix="/api/v1/shipments", tags=["shipments"])
NOT_IMPLEMENTED = {501: {"description": "Not implemented"}}

def _not_implemented():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented",)

@router.get("", response_model=list[ShipmentSchema], responses=NOT_IMPLEMENTED)
def list_shipments():
    _not_implemented()

@router.get("/{id}", response_model=ShipmentSchema, responses=NOT_IMPLEMENTED)
def get_shipment(id: int):
    _not_implemented()

@router.post("", status_code=status.HTTP_201_CREATED, responses=NOT_IMPLEMENTED,)
def create_shipment(data: dict):
    _not_implemented()

@router.put("/{id}", responses=NOT_IMPLEMENTED)
def update_shipment(id: int, data: dict):
    _not_implemented()

@router.delete("/{id}", responses=NOT_IMPLEMENTED)
def delete_shipment(id: int):
    _not_implemented()

@router.get("/{id}/orders", responses=NOT_IMPLEMENTED)
def list_shipment_orders(id: int):
    _not_implemented()

@router.put("/{id}/orders", responses=NOT_IMPLEMENTED)
def set_shipment_orders(id: int, data: list[int]):
    _not_implemented()

@router.get("/{id}/items", responses=NOT_IMPLEMENTED)
def list_shipment_items(id: int):
    _not_implemented()

@router.put("/{id}/items", responses=NOT_IMPLEMENTED)
def replace_shipment_items(id: int, data: list[dict]):
    _not_implemented()
