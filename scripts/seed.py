"""Load the v1 JSON files into the migrated database
"""
import json
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy import insert, text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from models import (  # noqa: E402
    Client, Inventory, Item, ItemGroup, ItemLine, ItemType, Location, Order, OrderItem,
    Shipment, ShipmentItem, Supplier, Transfer, TransferItem, User, Warehouse, get_engine,
)

data_dir = Path(sys.argv[1] if len(sys.argv) > 1 else "data")

# Parents first, so the foreign keys are satisfied.
TABLES = [Warehouse, Location, Supplier, Client, ItemGroup, ItemLine, ItemType, Item,
          Inventory, Order, OrderItem, Shipment, ShipmentItem, Transfer, TransferItem, User]

with get_engine().begin() as conn:
    for model in TABLES:
        name = model.__tablename__
        rows = json.loads((data_dir / f"{name}.json").read_text(encoding="utf-8"))
        for row in rows:
            for key, value in row.items():
                if key.endswith(("_at", "_date")):
                    row[key] = datetime.fromisoformat(value.replace("Z", "+00:00"))
        for i in range(0, len(rows), 5000):
            conn.execute(insert(model), rows[i : i + 5000])
        if "id" in model.__table__.c:
            conn.execute(text(f'SELECT setval(pg_get_serial_sequence(\'"{name}"\', \'id\'), '
                              f'(SELECT COALESCE(MAX(id), 1) FROM "{name}"))'))
        print(f"{name:<15} {len(rows)} rows")