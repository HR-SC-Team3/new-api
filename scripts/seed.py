"""Create the tables and load the JSON files
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import insert, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from models import (
    Base, Client, Inventory, Item, ItemGroup, ItemLine, ItemType, Location, Order,
    OrderItem, Shipment, ShipmentItem, Supplier, Transfer, TransferItem, User,
    Warehouse, get_engine,
)

parser = argparse.ArgumentParser()
parser.add_argument("data_dir", nargs="?", default="data", type=Path)
parser.add_argument("--reset", action="store_true", help="drop and recreate ALL tables")
args = parser.parse_args()

# Parents first
TABLES = [Warehouse, Location, Supplier, Client, ItemGroup, ItemLine, ItemType, Item,
          Inventory, Order, OrderItem, Shipment, ShipmentItem, Transfer, TransferItem, User]


def read(model):
    rows = json.loads((args.data_dir / f"{model.__tablename__}.json").read_text(encoding="utf-8"))
    for row in rows:
        for key, value in row.items():
            if key.endswith(("_at", "_date")):
                row[key] = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return rows


engine = get_engine()
if not args.reset:
    sys.exit("This drops all tables. Re-run with --reset to confirm.")
if engine.url.host not in ("localhost", "127.0.0.1"):
    sys.exit(f"Refusing to reset a non-local database ({engine.url.host}).")

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with engine.begin() as conn:
    for model in TABLES:
        rows = read(model)
        for i in range(0, len(rows), 5000):
            conn.execute(insert(model), rows[i : i + 5000])
        if "id" in model.__table__.c:
            name = model.__tablename__
            conn.execute(text(f'SELECT setval(pg_get_serial_sequence(\'"{name}"\', \'id\'), '
                              f'(SELECT COALESCE(MAX(id), 1) FROM "{name}"))'))
        print(f"{model.__tablename__:<15} {len(rows)} rows")