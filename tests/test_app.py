from http import HTTPStatus

import pytest
# Store endpoints
def test_create_store_and_get_store(client):
    # Create a store
    store_data = {"name": "Test Store"}
    response = client.post("/store", json=store_data)
    assert response.status_code == HTTPStatus.CREATED
    store = response.get_json()
    assert store["name"] == "Test Store"
    assert "id" in store

    # Get the store by id
    store_id = store["id"]
    response = client.get(f"/store/{store_id}")
    assert response.status_code == HTTPStatus.OK
    store_fetched = response.get_json()
    assert store_fetched["id"] == store_id
    assert store_fetched["name"] == "Test Store"

def test_get_stores_list(client):
    # Should return a list (may be empty or have stores from previous tests)
    response = client.get("/store")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.get_json(), list)

def test_delete_store(client):
    # Create a store
    store_data = {"name": "Delete Store"}
    response = client.post("/store", json=store_data)
    store_id = response.get_json()["id"]
    # Delete the store
    response = client.delete(f"/store/{store_id}")
    assert response.status_code == HTTPStatus.OK
    # API returns message without trailing period
    assert response.get_json()["message"] == "Store deleted"
    # Try to get the deleted store
    response = client.get(f"/store/{store_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND

# Item endpoints
def test_create_item_and_get_item(client):
    # Create a store first
    store_data = {"name": "Item Store"}
    store_resp = client.post("/store", json=store_data)
    store_id = store_resp.get_json()["id"]

    # Create an item
    item_data = {"name": "Test Item", "price": 9.99, "store_id": store_id}
    print("item_data:", item_data)
    response = client.post("/item", json=item_data)
    print("response data:", response.get_data(as_text=True))
    assert response.status_code == HTTPStatus.CREATED
    item = response.get_json()
    assert item["name"] == "Test Item"
    assert item["price"] == 9.99
    # API returns nested store object instead of store_id field
    assert item["store"]["id"] == store_id
    assert "id" in item

    # Get the item by id
    item_id = item["id"]
    response = client.get(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.OK
    item_fetched = response.get_json()
    assert item_fetched["id"] == item_id
    assert item_fetched["name"] == "Test Item"

def test_get_items_list(client):
    response = client.get("/item")
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.get_json(), list)

def test_delete_item(client):
    # Create a store and item
    store_resp = client.post("/store", json={"name": "Delete Item Store"})
    store_id = store_resp.get_json()["id"]
    item_resp = client.post("/item", json={"name": "Delete Me", "price": 1.23, "store_id": store_id})
    item_id = item_resp.get_json()["id"]
    # Delete the item
    response = client.delete(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.OK
    assert response.get_json()["message"] == "Item deleted."
    # Try to get the deleted item
    response = client.get(f"/item/{item_id}")
    assert response.status_code == HTTPStatus.NOT_FOUND
