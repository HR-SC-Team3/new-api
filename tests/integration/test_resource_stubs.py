import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

Resources = (
    "warehouses", "locations", "items", "item_lines", "item_groups",
    "item_types", "suppliers", "orders", "clients", "shipments", "transfers",
)

CRUD_operations = (
    ("GET", "", False),
    ("GET", "/1", False),
    ("POST", "", True),
    ("PUT", "/1", True),
    ("DELETE", "/1", False),
)

@pytest.mark.parametrize("resource", Resources)
@pytest.mark.parametrize(("method", "suffix", "needs_body"), CRUD_operations)
def test_resource_crud_stubs_return_501(resource, method, suffix, needs_body):
    path = f"/api/v1/{resource}{suffix}"
    body = {"id": 1, "code": "TEST"} if resource == "items" else {}

    kwargs = {"json": body} if needs_body else {}
    response = client.request(method, path, **kwargs)
    assert response.status_code == 501


@pytest.mark.parametrize(
    ("method", "body"),
    [("GET", None), ("POST", {}),],)

def test_inventory_collection_stubs_return_501(method, body):
    kwargs = {"json": body} if body is not None else {}
    response = client.request(method, "/api/v1/inventories", **kwargs)
    assert response.status_code == 501


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_inventory_by_id_returns_404(method):
    response = client.request(method, "/api/v1/inventories/1")
    assert response.status_code == 404

NESTED_STUBS = (
    ("GET", "/api/v1/warehouses/1/locations", None),
    ("GET", "/api/v1/items/1/inventory", None),
    ("GET", "/api/v1/items/1/inventory/totals", None),
    ("GET", "/api/v1/item_lines/1/items", None),
    ("GET", "/api/v1/item_groups/1/items", None),
    ("GET", "/api/v1/item_types/1/items", None),
    ("GET", "/api/v1/suppliers/1/items", None),
    ("GET", "/api/v1/orders/1/items", None),
    ("PUT", "/api/v1/orders/1/items", []),
    ("GET", "/api/v1/clients/1/orders", None),
    ("GET", "/api/v1/shipments/1/orders", None),
    ("PUT", "/api/v1/shipments/1/orders", []),
    ("GET", "/api/v1/shipments/1/items", None),
    ("PUT", "/api/v1/shipments/1/items", []),
    ("GET", "/api/v1/transfers/1/items", None),
    ("PUT", "/api/v1/transfers/1/commit", None),
)

@pytest.mark.parametrize(("method", "path", "body"), NESTED_STUBS)
def test_nested_stubs_return_501(method, path, body):
    kwargs = {"json": body} if body is not None else {}
    response = client.request(method, path, **kwargs)
    assert response.status_code == 501
