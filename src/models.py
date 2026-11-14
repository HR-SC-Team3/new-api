import os
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {datetime: DateTime(timezone=True), dict: JSONB}


def get_engine(url=None):
    url = url or os.environ["DATABASE_URL"].replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url)


def pk():
    return mapped_column(primary_key=True)


def fk(target):
    return mapped_column(ForeignKey(target), index=True)


class Warehouse(Base):
    __tablename__ = "warehouse"
    id: Mapped[int] = pk()
    code: Mapped[str]
    name: Mapped[str]
    address: Mapped[str]
    city: Mapped[str]
    zip_code: Mapped[str]
    province: Mapped[str]
    country: Mapped[str]
    contact_name: Mapped[str]
    contact_phone: Mapped[str]
    contact_email: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Location(Base):
    __tablename__ = "location"
    id: Mapped[int] = pk()
    warehouse_id: Mapped[int] = fk("warehouse.id")
    code: Mapped[str]
    name: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    outgoing_transfers: Mapped[list["Transfer"]] = relationship(
        back_populates="from_location",
        foreign_keys=lambda: [Transfer.from_location_id],
    )
    incoming_transfers: Mapped[list["Transfer"]] = relationship(
        back_populates="to_location",
        foreign_keys=lambda: [Transfer.to_location_id],
    )


class Supplier(Base):
    __tablename__ = "supplier"
    id: Mapped[int] = pk()
    code: Mapped[str]
    name: Mapped[str]
    address: Mapped[str]
    city: Mapped[str]
    zip_code: Mapped[str]
    province: Mapped[str]
    country: Mapped[str]
    contact_name: Mapped[str]
    phone_number: Mapped[str]
    reference: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Client(Base):
    __tablename__ = "client"
    id: Mapped[int] = pk()
    name: Mapped[str]
    address: Mapped[str]
    city: Mapped[str]
    zip_code: Mapped[str]
    province: Mapped[str]
    country: Mapped[str]
    contact_name: Mapped[str]
    contact_phone: Mapped[str]
    contact_email: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
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


class ItemGroup(Base):
    __tablename__ = "item_group"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class ItemLine(Base):
    __tablename__ = "item_line"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class ItemType(Base):
    __tablename__ = "item_type"
    id: Mapped[int] = pk()
    name: Mapped[str]
    description: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Item(Base):
    __tablename__ = "item"
    id: Mapped[int] = pk()
    code: Mapped[str]
    description: Mapped[str]
    barcode: Mapped[str]
    model_number: Mapped[str]
    commodity_code: Mapped[int]
    unit_weight: Mapped[Decimal] = mapped_column(Numeric(8, 3))
    item_line_id: Mapped[int] = fk("item_line.id")
    item_group_id: Mapped[int] = fk("item_group.id")
    item_type_id: Mapped[int] = fk("item_type.id")
    min_purchase_qty: Mapped[int]
    case_size: Mapped[int]
    packaging_type: Mapped[str]
    order_multiple: Mapped[int]
    supplier_id: Mapped[int] = fk("supplier.id")
    supplier_sku: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Inventory(Base):
    __tablename__ = "inventory"
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True, index=True)
    quantity_on_hand: Mapped[int]
    quantity_expected: Mapped[int]
    quantity_ordered: Mapped[int]
    quantity_allocated: Mapped[int]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = pk()
    client_id: Mapped[int] = fk("client.id")
    order_date: Mapped[datetime]
    request_date: Mapped[datetime]
    reference: Mapped[str]
    customer_po_number: Mapped[str]
    order_status: Mapped[str]
    shipping_notes: Mapped[str | None]
    warehouse_id: Mapped[int] = fk("warehouse.id")
    ship_to_client_id: Mapped[int] = fk("client.id")
    bill_to_client_id: Mapped[int] = fk("client.id")
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    client: Mapped["Client"] = relationship(
        back_populates="orders",
        foreign_keys=[client_id],
    )
    ship_to_client: Mapped["Client"] = relationship(
        back_populates="ship_to_orders",
        foreign_keys=[ship_to_client_id],
    )
    bill_to_client: Mapped["Client"] = relationship(
        back_populates="bill_to_orders",
        foreign_keys=[bill_to_client_id],
    )
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = pk()
    order_id: Mapped[int] = fk("order.id")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    order: Mapped["Order"] = relationship(back_populates="items")


class Shipment(Base):
    __tablename__ = "shipment"
    id: Mapped[int] = pk()
    reference: Mapped[str]
    order_id: Mapped[int] = fk("order.id")
    shipment_date: Mapped[datetime]
    shipment_type: Mapped[str]
    shipment_status: Mapped[str]
    carrier_name: Mapped[str]
    shipping_method: Mapped[str]
    payment_type: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]


class ShipmentItem(Base):
    __tablename__ = "shipment_item"
    id: Mapped[int] = pk()
    shipment_id: Mapped[int] = fk("shipment.id")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]


class Transfer(Base):
    __tablename__ = "transfer"
    id: Mapped[int] = pk()
    reference: Mapped[str]
    from_location_id: Mapped[int] = fk("location.id")
    to_location_id: Mapped[int] = fk("location.id")
    transfer_status: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
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
    transfer_id: Mapped[int] = fk("transfer.id")
    item_id: Mapped[int] = fk("item.id")
    amount: Mapped[int]


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = pk()
    api_key: Mapped[str]
    app: Mapped[str]
    endpoint_access: Mapped[dict]