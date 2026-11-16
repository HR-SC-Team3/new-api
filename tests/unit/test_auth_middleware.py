import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import auth
from permission_users import make_user_for_permutation


class FakeCache:
    """In-memory stand-in for the Redis helpers in cache.py."""

    def __init__(self):
        self.store = {}
        self.down = False

    def get_cached_user(self, api_key):
        return None if self.down else self.store.get(api_key)

    def set_cached_user(self, api_key, user):
        if not self.down:
            self.store[api_key] = user


@pytest.fixture
def fake_cache(monkeypatch):
    fake = FakeCache()
    monkeypatch.setattr(auth.cache, "get_cached_user", fake.get_cached_user)
    monkeypatch.setattr(auth.cache, "set_cached_user", fake.set_cached_user)
    return fake


@pytest.fixture
def db_users(monkeypatch):
    """Fake PostgreSQL: a dict of api_key -> user, plus a list of lookups."""
    users = {}
    lookups = []

    def load(api_key):
        lookups.append(api_key)
        return users.get(api_key)

    monkeypatch.setattr(auth, "_load_user_from_db", load)
    users["_lookups"] = lookups
    return users


@pytest.fixture
def client(fake_cache, db_users):
    app = FastAPI()
    app.middleware("http")(auth.auth_middleware)

    @app.get("/")
    def root():
        return {"ok": True}

    @app.get("/api/v1/warehouses")
    def list_warehouses():
        return []

    @app.post("/api/v1/warehouses")
    def create_warehouse():
        return {}

    return TestClient(app)


def _add_user(db_users, resource, method, allowed):
    user = make_user_for_permutation(resource, method, allowed)
    db_users[user["api_key"]] = {
        "app": user["app"],
        "endpoint_access": user["endpoint_access"],
    }
    return {auth.API_KEY_HEADER: user["api_key"]}


def test_missing_api_key_returns_401(client):
    assert client.get("/api/v1/warehouses").status_code == 401


def test_unknown_api_key_returns_401(client):
    # A generated key that is never added to db_users, so it stays unknown.
    unknown_key = make_user_for_permutation("warehouses", "get", True)["api_key"]
    response = client.get(
        "/api/v1/warehouses", headers={auth.API_KEY_HEADER: unknown_key}
    )
    assert response.status_code == 401


def test_allowed_method_returns_200(client, db_users):
    headers = _add_user(db_users, "warehouses", "get", True)
    assert client.get("/api/v1/warehouses", headers=headers).status_code == 200


def test_denied_method_returns_403(client, db_users):
    headers = _add_user(db_users, "warehouses", "post", False)
    assert client.post("/api/v1/warehouses", headers=headers).status_code == 403


def test_missing_resource_entry_is_denied(client, db_users):
    headers = _add_user(db_users, "warehouses", "get", True)
    key = headers[auth.API_KEY_HEADER]
    db_users[key]["endpoint_access"].pop("warehouses")
    assert client.get("/api/v1/warehouses", headers=headers).status_code == 403


def test_public_path_needs_no_key(client):
    assert client.get("/").status_code == 200


def test_cache_miss_request_succeeds(client, db_users):
    headers = _add_user(db_users, "warehouses", "get", True)
    response = client.get("/api/v1/warehouses", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_cache_hit_request_succeeds(client, db_users):
    headers = _add_user(db_users, "warehouses", "get", True)
    client.get("/api/v1/warehouses", headers=headers)
    response = client.get("/api/v1/warehouses", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    assert len(db_users["_lookups"]) == 1


def test_find_user_fills_cache_on_miss(db_users, fake_cache):
    headers = _add_user(db_users, "warehouses", "get", True)
    key = headers[auth.API_KEY_HEADER]
    assert auth.find_user(key) == db_users[key]
    assert fake_cache.store[key] == db_users[key]


def test_find_user_unknown_key_is_not_cached(db_users, fake_cache):
    key = make_user_for_permutation("warehouses", "get", True)["api_key"]
    assert auth.find_user(key) is None
    assert key not in fake_cache.store


def test_redis_down_falls_back_to_database(client, db_users, fake_cache):
    headers = _add_user(db_users, "warehouses", "get", True)
    fake_cache.down = True
    assert client.get("/api/v1/warehouses", headers=headers).status_code == 200
