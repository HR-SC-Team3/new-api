"""Create the tables and load the JSON files
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import insert, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from models import *
from models import Base, get_engine

data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")

# Parents first
TABLES = [Warehouse, Location, Supplier, Client, ItemGroup, ItemLine, ItemType, Item,  # noqa: F405
          Inventory, Order, OrderItem, Shipment, ShipmentItem, Transfer, TransferItem, User]  # noqa: F405


def read(model):
    rows = json.loads((data_dir / f"{model.__tablename__}.json").read_text(encoding="utf-8"))
    for row in rows:
        for key, value in row.items():
            if key.endswith(("_at", "_date")):
                row[key] = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return rows


engine = get_engine()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with engine.begin() as conn:
    for model in TABLES:
        rows = read(model)
        for i in range(0, len(rows), 5000):
            conn.execute(insert(model), rows[i : i + 5000])
        if engine.dialect.name == "postgresql" and "id" in model.__table__.c:
            conn.execute(text(f'SELECT setval(pg_get_serial_sequence(\'"{model.__tablename__}"\', \'id\'), '
                              f'(SELECT COALESCE(MAX(id), 1) FROM "{model.__tablename__}"))'))
        print(f"{model.__tablename__:<15} {len(rows)} rows")