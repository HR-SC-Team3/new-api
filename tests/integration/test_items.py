import json
import time
from pathlib import Path

import pytest
import requests

import uuid

from schemas import Item


REPO_ROOT = Path(__file__).resolve().parents[2]
ITEMS_MODEL_SOURCE = (
    REPO_ROOT  / "src" / "models.py"
).read_text(encoding="utf-8")


# region Shared helpers

def _url(base_url, path=""):
    return f"{base_url}/api/v1/items{path}"


def _get_headers(user_headers, method="get", allowed=True):
    return user_headers(resource="items", method=method, allowed=allowed)

def _unique_item_id(base_url, user_headers):
    headers = _get_headers(user_headers)

    while True:
        item_id = uuid.uuid4().int % 1_000_000_000 + 1_000_000_000

        response = requests.get(
            _url(base_url, f"/{item_id}"),
            headers=headers,
        )

        if response.status_code == 404:
            return item_id

        assert response.status_code == 200, response.text

@pytest.fixture
def test_item(base_url, user_headers):
    item_id = _unique_item_id(base_url, user_headers)
    
    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Temporary Test Item",
        "barcode": f"TEST-{item_id}",
        "model_number": f"MODEL-{item_id}",
        "commodity_code": 12345,
        "unit_weight": 1.5,
        "item_line_id": 1,
        "item_group_id": 1,
        "item_type_id": 1,
        "min_purchase_qty": 1,
        "case_size": 1,
        "packaging_type": "Box",
        "order_multiple": 1,
        "supplier_id": 1,
        "supplier_sku": f"SKU-{item_id}",
    }

    response = requests.post(
        _url(base_url),
        headers=_get_headers(user_headers, method="post"),
        json=payload,
    )

    assert response.status_code == 201, response.text

    created_item = response.json()

    yield created_item

    delete_response = requests.delete(
        _url(base_url, f"/{created_item['id']}"),
        headers=_get_headers(user_headers, method="delete"),
    )

    assert delete_response.status_code in (200, 204, 404)
    
@pytest.fixture
def cleanup_items(base_url, user_headers):
    item_ids = []

    yield item_ids

    headers = _get_headers(user_headers, method="delete")

    for item_id in item_ids:
        requests.delete(
            _url(base_url, f"/{item_id}"),
            headers=headers,
        )

# endregion


# region GET /items


def test_get_items_returns_200_with_valid_response(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(_url(base_url), headers=headers)

    assert response.status_code == 200

    body = response.json()

    assert isinstance(body, list)
    assert len(body) > 0
    assert "id" in body[0]


def test_response_body_matches_documented_schema(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(_url(base_url), headers=headers)

    body = response.json()

    for raw in body:
        Item.model_validate(raw)


def test_response_content_type_is_json(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(_url(base_url), headers=headers)

    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")


def test_response_time_is_reasonable(base_url, user_headers):
    headers = _get_headers(user_headers)

    start = time.monotonic()

    response = requests.get(_url(base_url), headers=headers)

    elapsed = time.monotonic() - start

    assert response.status_code == 200
    assert (
        elapsed < 0.5
    ), f"GET /items took {elapsed:.2f}s, which is unreasonably slow"


@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"page": 1}, id="pagination-page"),
        pytest.param({"limit": 5}, id="pagination-limit"),
        pytest.param({"supplier_id": 17}, id="filter-supplier"),
        pytest.param({"item_group_id": 1}, id="filter-item-group"),
        pytest.param({"sort": "description"}, id="sort-description"),
        pytest.param({"page": -1}, id="invalid-negative-page"),
        pytest.param({"totally_unknown_key": "x"}, id="unknown-key"),
    ],
)
def test_query_params_are_ignored(base_url, user_headers, params):
    headers = _get_headers(user_headers)

    baseline = requests.get(_url(base_url), headers=headers)
    response = requests.get(_url(base_url), headers=headers, params=params)

    assert response.status_code == 200
    assert response.json() == baseline.json()


@pytest.mark.xfail(
    strict=True,
    reason="Query parameters are ignored, so pagination is not honoured.",
)
def test_query_param_limit_is_honoured(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(_url(base_url), headers=headers, params={"limit": 1})

    assert response.status_code == 200
    assert len(response.json()) <= 1


@pytest.mark.xfail(
    strict=True,
    reason="API does not support supplier_id query filtering",
)
def test_filter_supplier_returns_matching_items(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url),
        headers=headers,
        params={"supplier_id": 17},
    )

    assert response.status_code == 200

    body = response.json()

    for item in body:
        assert item["supplier_id"] == 17


@pytest.mark.xfail(
    strict=True,
    reason="API does not support item_group_id query filtering",
)
def test_filter_item_group_returns_matching_items(base_url, user_headers):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url),
        headers=headers,
        params={"item_group_id": 1},
    )

    assert response.status_code == 200

    body = response.json()

    for item in body:
        assert item["item_group_id"] == 1


@pytest.mark.xfail(
    strict=True,
    reason="Query parameters are ignored, so this is not honoured",
)
def test_sort_description_returns_correctly_ordered_results(
    base_url, user_headers
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url),
        headers=headers,
        params={"sort": "description"},
    )

    assert response.status_code == 200

    body = response.json()

    descriptions = [
        item["description"]
        for item in body
        if "description" in item
    ]

    assert descriptions == sorted(descriptions)


@pytest.mark.xfail(
    strict=True,
    reason="Query parameters are ignored, so this is not honoured",
)
def test_empty_result_set_returns_200_with_empty_array(
    base_url, user_headers
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url),
        headers=headers,
        params={"supplier_id": 999999},
    )

    assert response.status_code == 200
    assert response.json() == []


def test_missing_api_key_is_rejected_with_401(base_url):
    response = requests.get(_url(base_url))

    assert response.status_code == 401


def test_invalid_api_key_is_rejected_with_401(base_url):
    response = requests.get(
        _url(base_url),
        headers={"API_KEY": "not-a-real-key"},
    )

    assert response.status_code == 401


def test_insufficient_permissions_returns_403(base_url, user_headers):
    headers = _get_headers(user_headers, allowed=False)

    response = requests.get(
        _url(base_url),
        headers=headers,
    )

    assert response.status_code == 403


@pytest.mark.xfail(
    strict=True,
    reason=(
        "Error responses should use the same JSON error schema as "
        "successful responses."
    ),
)
def test_error_response_has_consistent_json_schema(base_url):
    response = requests.get(_url(base_url))

    assert response.status_code == 401
    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")

    body = response.json()

    assert "error" in body


def test_error_response_leaks_no_internal_details(base_url):
    response = requests.get(_url(base_url))

    text_lower = response.text.lower()

    for leak_indicator in (
        "traceback",
        "exception",
        "stack",
        "internal",
        "sql",
        'file "',
        "line ",
    ):
        assert leak_indicator not in text_lower


# endregion


# region GET /items/{id}


def test_get_item_by_id_returns_200_with_correct_resource(
    base_url, user_headers, test_item
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url, f"/{test_item['id']}"),
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json() == test_item


def test_get_item_by_id_matches_documented_schema(
    base_url, user_headers, test_item
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url, f"/{test_item['id']}"),
        headers=headers,
    )

    Item.model_validate(response.json())


def test_get_item_by_nonexistent_id_returns_404(
    base_url, user_headers
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url, "/999999"),
        headers=headers,
    )

    assert response.status_code == 404


def test_get_item_by_malformed_id_returns_400(
    base_url, user_headers
):
    headers = _get_headers(user_headers)

    response = requests.get(
        _url(base_url, "/not-an-id"),
        headers=headers,
    )

    assert response.status_code == 400


def test_get_item_requires_authentication(base_url):
    response = requests.get(_url(base_url, "/1"))

    assert response.status_code == 401


def test_get_item_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        allowed=False,
    )

    response = requests.get(
        _url(base_url, "/1"),
        headers=headers,
    )

    assert response.status_code == 403


def test_get_item_response_content_type_is_json(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}"),
        headers=_get_headers(user_headers),
    )

    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")


def test_get_item_malformed_id_error_leaks_no_internal_details(
    base_url, user_headers
):
    response = requests.get(
        _url(base_url, "/not-an-id"),
        headers=_get_headers(user_headers),
    )

    text_lower = response.text.lower()

    for leak_indicator in (
        "traceback",
        "exception",
        "valueerror",
        'file "',
        "line ",
    ):
        assert leak_indicator not in text_lower


# endregion


# region POST /items


def test_post_item_returns_created_resource_with_id(
    base_url, user_headers, cleanup_items
):
    item_id = _unique_item_id(base_url, user_headers)

    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Test Item",
    }

    headers = _get_headers(
        user_headers,
        method="post",
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json=payload,
    )
    
    if response.status_code == 201:
        cleanup_items.append(item_id)

    assert response.status_code == 201

    body = response.json()

    assert "id" in body
    assert body["id"] == item_id
    assert body["description"] == "Test Item"


def test_post_item_response_points_to_new_resource(
    base_url, user_headers, cleanup_items
):
    item_id = _unique_item_id(base_url, user_headers)

    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Location Test Item",
    }

    headers = _get_headers(
        user_headers,
        method="post",
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json=payload,
    )
    
    if response.status_code == 201:
        cleanup_items.append(item_id)

    assert response.status_code == 201

    assert (
        "Location" in response.headers
        or response.json().get("id") == item_id
    )


def test_post_item_missing_required_fields_returns_400(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    headers = _get_headers(
        user_headers,
        method="post",
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json={},
    )

    assert response.status_code in (400, 422)


def test_post_item_invalid_field_type_is_rejected(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    headers = _get_headers(
        user_headers,
        method="post",
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json={
            "id": "not-an-int",
            "code": "ITM-BAD",
            "description": "Bad Type Item",
        },
    )

    assert response.status_code in (400, 422)

def test_post_item_duplicate_id_returns_conflict(
    base_url, user_headers, test_item
):

    existing = test_item

    headers = _get_headers(
        user_headers,
        method="post",
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json={
            **existing,
            "description": "Duplicate Item",
        },
    )

    assert response.status_code in (400, 409, 422)


def test_post_item_is_immediately_retrievable(
    base_url, user_headers, cleanup_items
):
    item_id = _unique_item_id(base_url, user_headers)

    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Retrievable Item",
    }

    create_response = requests.post(
        _url(base_url),
        headers=_get_headers(user_headers, method="post"),
        json=payload,
    )
    
    if create_response.status_code == 201:
        cleanup_items.append(item_id)

    assert create_response.status_code == 201

    get_response = requests.get(
        _url(base_url, f"/{item_id}"),
        headers=_get_headers(user_headers),
    )

    assert get_response.status_code == 200
    assert get_response.json() is not None
    assert get_response.json()["description"] == "Retrievable Item"


@pytest.mark.parametrize(
    "foreign_key",
    [
        "item_line_id",
        "item_group_id",
        "item_type_id",
        "supplier_id",
    ],
)
def test_post_item_invalid_foreign_key_is_rejected(
    base_url,
    user_headers,
    cleanup_items,
    foreign_key,
):
    item_id = _unique_item_id(base_url, user_headers)

    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Invalid Foreign Key Test",
        foreign_key: 999999,
    }

    response = requests.post(
        _url(base_url),
        headers=_get_headers(user_headers, method="post"),
        json=payload,
    )
    
    if response.status_code == 201:
        cleanup_items.append(item_id)

    assert response.status_code in (400, 404, 409, 422)


def test_post_item_requires_authentication(base_url):
    response = requests.post(
        _url(base_url),
        json={"description": "No Auth Item"},
    )

    assert response.status_code == 401


def test_post_item_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        method="post",
        allowed=False,
    )

    response = requests.post(
        _url(base_url),
        headers=headers,
        json={"description": "Forbidden Item"},
    )

    assert response.status_code == 403


def test_post_item_wrong_content_type_is_rejected(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    headers = {
        **_get_headers(user_headers, method="post"),
        "Content-Type": "text/plain",
    }

    response = requests.post(
        _url(base_url),
        headers=headers,
        data=json.dumps({"description": "Plain Text Item"}),
    )

    assert response.status_code == 415


def test_post_item_malformed_json_body_returns_400(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    headers = {
        **_get_headers(user_headers, method="post"),
        "Content-Type": "application/json",
    }

    response = requests.post(
        _url(base_url),
        headers=headers,
        data="{not valid json",
    )

    assert response.status_code in (400, 422)


def test_post_item_malformed_json_body_leaks_no_internal_details(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    headers = {
        **_get_headers(user_headers, method="post"),
        "Content-Type": "application/json",
    }

    response = requests.post(
        _url(base_url),
        headers=headers,
        data="{not valid json",
    )

    text_lower = response.text.lower()

    for leak_indicator in (
        "traceback",
        "exception",
        "jsondecodeerror",
        'file "',
        "line ",
    ):
        assert leak_indicator not in text_lower


# endregion


# region PUT /items/{id}


def test_put_item_valid_payload_returns_200(
    base_url, user_headers, test_item
):

    existing = test_item

    updated = {
        **existing,
        "description": "Updated Item",
    }

    response = requests.put(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="put"),
        json=updated,
    )

    assert response.status_code == 200


def test_put_item_update_is_persisted(
    base_url, user_headers, test_item
):

    existing = test_item

    updated = {
        **existing,
        "description": "Persisted Item",
    }

    put_response = requests.put(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="put"),
        json=updated,
    )

    assert put_response.status_code == 200

    get_response = requests.get(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers),
    )

    assert get_response.json()["description"] == "Persisted Item"


def test_put_item_nonexistent_id_returns_404(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    updated = {
        "id": 999999,
        "code": "ITM-999999",
        "description": "Ghost Item",
    }

    response = requests.put(
        _url(base_url, "/999999"),
        headers=_get_headers(user_headers, method="put"),
        json=updated,
    )

    assert response.status_code == 404


def test_put_item_malformed_id_returns_400(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    payload = {
        "id": 1,
        "code": "ITM-000001",
        "description": "Malformed ID Test",
    }

    response = requests.put(
        _url(base_url, "/not-an-id"),
        headers=_get_headers(user_headers, method="put"),
        json=payload,
    )

    assert response.status_code == 400


def test_put_item_invalid_field_type_is_rejected(
    base_url, user_headers, test_item
):

    existing = test_item

    updated = {
        **existing,
        "unit_weight": "not-a-number",
    }

    response = requests.put(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="put"),
        json=updated,
    )

    assert response.status_code in (400, 422)


@pytest.mark.parametrize(
    "foreign_key",
    [
        "item_line_id",
        "item_group_id",
        "item_type_id",
        "supplier_id",
    ],
)
def test_put_item_invalid_foreign_key_is_rejected(
    base_url,
    user_headers,
    test_item,
    foreign_key,
):

    existing = test_item

    updated = {
        **existing,
        foreign_key: 999999,
    }

    response = requests.put(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="put"),
        json=updated,
    )

    assert response.status_code in (400, 404, 409, 422)


def test_put_item_requires_authentication(base_url):
    response = requests.put(
        _url(base_url, "/1"),
        json={"description": "No Auth Item"},
    )

    assert response.status_code == 401


def test_put_item_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        method="put",
        allowed=False,
    )

    response = requests.put(
        _url(base_url, "/1"),
        headers=headers,
        json={"description": "Forbidden Item"},
    )

    assert response.status_code == 403


# endregion


# region DELETE /items/{id}

def test_delete_item_valid_id_returns_200(
    base_url, user_headers, test_item
):

    existing = test_item

    response = requests.delete(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="delete"),
    )

    assert response.status_code in (200, 204)


def test_delete_item_resource_is_actually_gone(
    base_url, user_headers, test_item
):

    existing = test_item

    delete_response = requests.delete(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers, method="delete"),
    )

    assert delete_response.status_code in (200, 204)

    get_response = requests.get(
        _url(base_url, f"/{existing['id']}"),
        headers=_get_headers(user_headers),
    )

    assert get_response.status_code == 404


def test_delete_item_nonexistent_id_returns_404(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    response = requests.delete(
        _url(base_url, "/999999"),
        headers=_get_headers(user_headers, method="delete"),
    )

    assert response.status_code == 404

def test_delete_item_malformed_id_returns_400(
    base_url, user_headers, preserve_data_files
):
    preserve_data_files("item.json")

    response = requests.delete(
        _url(base_url, "/not-an-id"),
        headers=_get_headers(user_headers, method="delete"),
    )

    assert response.status_code == 400


def test_delete_item_repeated_delete_returns_404(
    base_url, user_headers, test_item
):

    existing = test_item

    headers = _get_headers(
        user_headers,
        method="delete",
    )

    first = requests.delete(
        _url(base_url, f"/{existing['id']}"),
        headers=headers,
    )

    second = requests.delete(
        _url(base_url, f"/{existing['id']}"),
        headers=headers,
    )

    assert first.status_code in (200, 204)
    assert second.status_code == 404


def test_delete_item_requires_authentication(base_url):
    response = requests.delete(
        _url(base_url, "/1"),
    )

    assert response.status_code == 401


def test_delete_item_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        method="delete",
        allowed=False,
    )

    response = requests.delete(
        _url(base_url, "/1"),
        headers=headers,
    )

    assert response.status_code == 403




# endregion


# region GET /items/{id}/inventory


def test_get_item_inventory_returns_200(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}/inventory"),
        headers=_get_headers(user_headers),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_item_inventory_only_returns_correct_item_inventory(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}/inventory"),
        headers=_get_headers(user_headers),
    )

    assert response.status_code == 200

    body = response.json()

    for inventory in body:
        if isinstance(inventory, dict):
            if "item_id" in inventory:
                assert inventory["item_id"] == test_item["id"]


def test_get_item_inventory_nonexistent_item_returns_404(
    base_url, user_headers
):
    response = requests.get(
        _url(base_url, "/999999/inventory"),
        headers=_get_headers(user_headers),
    )

    assert response.status_code == 404


def test_get_item_inventory_requires_authentication(base_url):
    response = requests.get(
        _url(base_url, "/1/inventory"),
    )

    assert response.status_code == 401


def test_get_item_inventory_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        allowed=False,
    )

    response = requests.get(
        _url(base_url, "/1/inventory"),
        headers=headers,
    )

    assert response.status_code == 403


def test_get_item_inventory_response_content_type_is_json(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}/inventory"),
        headers=_get_headers(user_headers),
    )

    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")


# endregion


# region GET /items/{id}/inventory/totals


def test_get_item_inventory_totals_returns_200(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}/inventory/totals"),
        headers=_get_headers(user_headers),
    )

    assert response.status_code == 200


def test_get_item_inventory_totals_nonexistent_item_returns_404(
    base_url, user_headers
):
    response = requests.get(
        _url(base_url, "/999999/inventory/totals"),
        headers=_get_headers(user_headers),
    )

    assert response.status_code == 404


def test_get_item_inventory_totals_requires_authentication(
    base_url
):
    response = requests.get(
        _url(base_url, "/1/inventory/totals"),
    )

    assert response.status_code == 401


def test_get_item_inventory_totals_insufficient_permissions_returns_403(
    base_url, user_headers
):
    headers = _get_headers(
        user_headers,
        allowed=False,
    )

    response = requests.get(
        _url(base_url, "/1/inventory/totals"),
        headers=headers,
    )

    assert response.status_code == 403


def test_get_item_inventory_totals_response_content_type_is_json(
    base_url, user_headers, test_item
):

    response = requests.get(
        _url(base_url, f"/{test_item['id']}/inventory/totals"),
        headers=_get_headers(user_headers),
    )

    assert response.headers.get(
        "Content-Type", ""
    ).startswith("application/json")


# endregion


# region Range validation


@pytest.mark.parametrize(
    "override, expected_message",
    [
        ({"id": 0}, "greater than 0"),
        ({"case_size": 0}, "greater than 0"),
        ({"order_multiple": -1}, "greater than 0"),
        ({"unit_weight": -0.1}, "greater than or equal to 0"),
    ],
)
def test_post_item_rejects_out_of_range_values(
    base_url, user_headers, cleanup_items, override, expected_message
):
    item_id = _unique_item_id(base_url, user_headers)

    payload = {
        "id": item_id,
        "code": f"ITM-{item_id}",
        "description": "Range Validation Test",
        **override,
    }

    response = requests.post(
        _url(base_url),
        headers=_get_headers(user_headers, method="post"),
        json=payload,
    )
    
    if response.status_code == 201 and payload["id"] != 0:
        cleanup_items.append(payload["id"])

    assert response.status_code == 422
    assert expected_message in response.json()["error"]

# endregion
