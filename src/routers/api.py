from fastapi import APIRouter

from src.routers.clients import router as clients_router
from src.routers.inventories import router as inventories_router
from src.routers.item_groups import router as item_groups_router
from src.routers.item_lines import router as item_lines_router
from src.routers.item_types import router as item_types_router
from src.routers.items import router as items_router
from src.routers.locations import router as locations_router
from src.routers.orders import router as orders_router
from src.routers.shipments import router as shipments_router
from src.routers.suppliers import router as suppliers_router
from src.routers.transfers import router as transfers_router
from src.routers.warehouses import router as warehouses_router

api_router = APIRouter()

for resource_router in (
    warehouses_router,
    locations_router,
    items_router,
    item_lines_router,
    item_groups_router,
    item_types_router,
    inventories_router,
    suppliers_router,
    orders_router,
    clients_router,
    shipments_router,
    transfers_router,
):
    api_router.include_router(resource_router)
