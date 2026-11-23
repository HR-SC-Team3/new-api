from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from models import (
    Item as ItemModel,
    Inventory as InventoryModel,
    ItemLine,
    ItemGroup,
    ItemType,
    Supplier,
)

from db import get_session_factory

from schema_validations import (
    Item as ItemSchema,
    ItemInput,
    Inventory as InventorySchema,
)

router = APIRouter(prefix="/api/v1/items", tags=["items"])

def parse_id(id: str) -> int:
    try:
        return int(id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid item ID",
        )


def check_foreign_keys(session, data):
    foreign_keys = {
        "item_line_id": ItemLine,
        "item_group_id": ItemGroup,
        "item_type_id": ItemType,
        "supplier_id": Supplier,
    }

    for field, model in foreign_keys.items():
        value = getattr(data, field)

        if value is not None and session.get(model, value) is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field}",
            )


@router.get("", response_model=list[ItemSchema])
def list_items():
    with get_session_factory()() as session:
        items = session.query(ItemModel).order_by(ItemModel.id).all()

        return items


@router.get("/{id}", response_model=ItemSchema)
def get_item(id: str):
    item_id = parse_id(id)

    with get_session_factory()() as session:
        item = session.get(ItemModel, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        return item


@router.post("", response_model=ItemSchema, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemInput, response: Response):
    with get_session_factory()() as session:

        # Check whether the item ID already exists.
        if session.get(ItemModel, data.id) is not None:
            raise HTTPException(
                status_code=409,
                detail="Item already exists",
            )

        check_foreign_keys(session, data)

        item = ItemModel(**data.model_dump())

        try:
            session.add(item)
            session.commit()
            session.refresh(item)

        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Could not create item because of a database constraint",
            )

        response.headers["Location"] = f"/api/v1/items/{item.id}"

        return item


@router.put("/{id}", response_model=ItemSchema)
def save_item(id: str, data: ItemInput):
    item_id = parse_id(id)

    with get_session_factory()() as session:

        item = session.get(ItemModel, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        if data.id != item_id:
            raise HTTPException(
                status_code=400,
                detail="The item ID in the body must match the URL",
            )

        check_foreign_keys(session, data)

        for field, value in data.model_dump().items():
            setattr(item, field, value)

        try:
            session.commit()
            session.refresh(item)

        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Could not update item because of a database constraint",
            )

        return item


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def delete_item(id: str):
    item_id = parse_id(id)

    with get_session_factory()() as session:

        item = session.get(ItemModel, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        try:
            session.delete(item)
            session.commit()

        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="Cannot delete item because it is being used by another resource",
            )

        return {"detail": "Item deleted successfully"}


@router.get(
    "/{id}/inventory",
    response_model=list[InventorySchema],
    tags=["inventories"],
)
def get_item_inventory(id: str):
    item_id = parse_id(id)

    with get_session_factory()() as session:

        item = session.get(ItemModel, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        inventory = (
            session.query(InventoryModel)
            .filter(InventoryModel.item_id == item_id)
            .all()
        )

        result = []

        for record in inventory:
            result.append({
                "item_id": record.item_id,
                "location_id": record.location_id,
                "quantity_on_hand": record.quantity_on_hand or 0,
                "quantity_expected": record.quantity_expected or 0,
                "quantity_ordered": record.quantity_ordered or 0,
                "quantity_allocated": record.quantity_allocated or 0,
                "created_at": record.created_at,
                "updated_at": record.updated_at,
            })

        return result


@router.get("/{id}/inventory/totals", tags=["inventories"],)
def get_item_inventory_totals(id: str):
    item_id = parse_id(id)

    with get_session_factory()() as session:

        item = session.get(ItemModel, item_id)

        if item is None:
            raise HTTPException(
                status_code=404,
                detail="Item not found",
            )

        totals = (
            session.query(
                func.coalesce(
                    func.sum(InventoryModel.quantity_on_hand), 0
                ).label("quantity_on_hand"),

                func.coalesce(
                    func.sum(InventoryModel.quantity_expected), 0
                ).label("quantity_expected"),

                func.coalesce(
                    func.sum(InventoryModel.quantity_ordered), 0
                ).label("quantity_ordered"),

                func.coalesce(
                    func.sum(InventoryModel.quantity_allocated), 0
                ).label("quantity_allocated"),
            )
            .filter(InventoryModel.item_id == item_id)
            .one()
        )

        return {
            "item_id": item_id,
            "quantity_on_hand": totals.quantity_on_hand,
            "quantity_expected": totals.quantity_expected,
            "quantity_ordered": totals.quantity_ordered,
            "quantity_allocated": totals.quantity_allocated,
        }
