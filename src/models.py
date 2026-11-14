import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True), dict: JSONB}


def get_engine(url=None):
    url = url or os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url)


def pk():
    return mapped_column(primary_key=True)


def fk(target, ondelete=None):
    """Foreign key with an index. Nullable or not follows the Mapped[...] annotation.
    ondelete=None means the database default (NO ACTION): a parent that still has
    children cannot be deleted."""
    return mapped_column(ForeignKey(target, ondelete=ondelete), index=True)


class Timestamps:
    """Set by the database when the API does not send them."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


# Nullability follows api-doc.yml: fields that the *Input schema does not require
# are nullable, so a create request with only the required fields is accepted.


class Warehouse(Timestamps, Base):
    __tablename__ = "warehouse"
    id: Mapped[int] = pk()
    code: Mapped[str]
    name: Mapped[str]
    address: Mapped[str | None]
    city: Mapped[str | None]
    zip_code: Mapped[str | None]
    province: Mapped[str | None]
    country: Mapped[str | None]
    contact_name: Mapped[str | None]
    contact_phone: Mapped[str | None]
    contact_email: Mapped[str | None]


class Location(Timestamps, Base):
    __tablename__ = "location"
    id: Mapped[int] = pk()
    warehouse_id: Mapped[int] = fk("warehouse.id")
    code: Mapped[str]
    name: Mapped[str | None]
    outgoing_transfers: Mapped[list["Transfer"]] = relationship(
        back_populates="from_location",
        foreign_keys=lambda: [Transfer.from_location_id],
    )
    incoming_transfers: Mapped[list["Transfer"]] = relationship(
        back_populates="to_location",
        foreign_keys=lambda: [Transfer.to_location_id],
    )


class Supplier(Timestamps, Base):
    __tablename__ = "supplier"
    id: Mapped[int] = pk()
    code: Mapped[str]
    name: Mapped[str]
    address: Mapped[str | None]
    city: Mapped[str | None]
    zip_code: Mapped[str | None]
    province: Mapped[str | None]
    country: Mapped[str | None]
    contact_name: Mapped[str | None]
    phone_number: Mapped[str | None]
    reference: Mapped[str | None]


class Client(Timestamps, Base):
    __tablename__ = "client"
    id: Mapped[int] = pk()
    name: Mapped[str]
    address: Mapped[str | None]
    city: Mapped[str | None]
    zip_code: Mapped[str | None]
    province: Mapped[str | None]
    country: Mapped[str | None]
    contact_name: Mapped[str | None]
    contact_phone: Mapped[str | None]
    contact_email: Mapped[str | None]
    orders: Mapped[list["Order"]] = relationship(
        back_populates="client",
        foreign_keys=lambda: [Order.client_id],
    )
    ship_to_orders: Mapped[list["Order"]] = relationship(
        back_populates="ship_to_client",
        foreign_keys=lambda: [Order.ship_to_client_id],
    )
    bill_to_orders: Mapped[list["Order"]] = relationship(
        back_populates="bill_to_client",
        foreign_keys=lambda: [Order.bill_to_client_id],
    )


class ItemGroup(Timestamps, Base):
    __tablename__ = "item_group"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str | None]


class ItemLine(Timestamps, Base):
    __tablename__ = "item_line"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str | None]


class ItemType(Timestamps, Base):
    __tablename__ = "item_type"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str | None]


class Item(Timestamps, Base):
    __tablename__ = "item"
    id: Mapped[int] = pk()
    code: Mapped[str]
    description: Mapped[str | None]
    barcode: Mapped[str | None]
    model_number: Mapped[str | None]
    commodity_code: Mapped[int | None]
    unit_weight: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    item_line_id: Mapped[int | None] = fk("item_line.id")
    item_group_id: Mapped[int | None] = fk("item_group.id")
    item_type_id: Mapped[int | None] = fk("item_type.id")
    min_purchase_qty: Mapped[int | None]
    case_size: Mapped[int | None]
    packaging_type: Mapped[str | None]
    order_multiple: Mapped[int | None]
    supplier_id: Mapped[int | None] = fk("supplier.id")
    supplier_sku: Mapped[str | None]


class Inventory(Timestamps, Base):
    __tablename__ = "inventory"
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True, index=True)
    quantity_on_hand: Mapped[int | None]
    quantity_expected: Mapped[int | None]
    quantity_ordered: Mapped[int | None]
    quantity_allocated: Mapped[int | None]


class Order(Timestamps, Base):
    __tablename__ = "order"
    id: Mapped[int] = pk()
    client_id: Mapped[int] = fk("client.id")
    order_date: Mapped[datetime | None]
    request_date: Mapped[datetime | None]
    reference: Mapped[str | None]
    customer_po_number: Mapped[str | None]
    order_status: Mapped[str | None]
    shipping_notes: Mapped[str | None]
    warehouse_id: Mapped[int | None] = fk("warehouse.id")
    ship_to_client_id: Mapped[int | None] = fk("client.id")
    bill_to_client_id: Mapped[int | None] = fk("client.id")
    client: Mapped["Client"] = relationship(
        back_populates="orders",
        foreign_keys=[client_id],
    )
    ship_to_client: Mapped["Client | None"] = relationship(
        back_populates="ship_to_orders",
        foreign_keys=[ship_to_client_id],
    )
    bill_to_client: Mapped["Client | None"] = relationship(
        back_populates="bill_to_orders",
        foreign_keys=[bill_to_client_id],
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = pk()
    order_id: Mapped[int] = fk("order.id", ondelete="CASCADE")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    order: Mapped["Order"] = relationship(back_populates="items")


class Shipment(Timestamps, Base):
    __tablename__ = "shipment"
    id: Mapped[int] = pk()
    reference: Mapped[str]
    order_id: Mapped[int | None] = fk("order.id")
    shipment_date: Mapped[datetime | None]
    shipment_type: Mapped[str | None]
    shipment_status: Mapped[str | None]
    carrier_name: Mapped[str | None]
    shipping_method: Mapped[str | None]
    payment_type: Mapped[str | None]


class ShipmentItem(Base):
    __tablename__ = "shipment_item"
    id: Mapped[int] = pk()
    shipment_id: Mapped[int] = fk("shipment.id", ondelete="CASCADE")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]


class Transfer(Timestamps, Base):
    __tablename__ = "transfer"
    id: Mapped[int] = pk()
    reference: Mapped[str]
    from_location_id: Mapped[int] = fk("location.id")
    to_location_id: Mapped[int] = fk("location.id")
    transfer_status: Mapped[str | None]
    from_location: Mapped["Location"] = relationship(
        back_populates="outgoing_transfers",
        foreign_keys=[from_location_id],
    )
    to_location: Mapped["Location"] = relationship(
        back_populates="incoming_transfers",
        foreign_keys=[to_location_id],
    )


class TransferItem(Base):
    __tablename__ = "transfer_item"
    id: Mapped[int] = pk()
    transfer_id: Mapped[int] = fk("transfer.id", ondelete="CASCADE")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = pk()
    api_key: Mapped[str]
    app: Mapped[str]
    endpoint_access: Mapped[dict]