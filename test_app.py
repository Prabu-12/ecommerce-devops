import pytest
from fastapi.testclient import TestClient
from app import app, products_db, orders_db, users_db

client = TestClient(app)

# ── Helper to reset state between tests ────────────
@pytest.fixture(autouse=True)
def clear_db():
    """Clear all databases before each test."""
    products_db.clear()
    orders_db.clear()
    users_db.clear()
    yield
    products_db.clear()
    orders_db.clear()
    users_db.clear()

# ── Root & Health ───────────────────────────────────
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["app"] == "E-Commerce API"

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"

# ── Products ────────────────────────────────────────
def test_get_products_empty():
    response = client.get("/products")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_create_product():
    response = client.post("/products", json={
        "name": "Laptop", "price": 999.99,
        "stock": 10, "category": "Electronics"
    })
    assert response.status_code == 201
    assert response.json()["product"]["name"] == "Laptop"

def test_get_product_by_id():
    create = client.post("/products", json={
        "name": "Phone", "price": 499.99,
        "stock": 5, "category": "Electronics"
    })
    product_id = create.json()["product"]["id"]
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Phone"

def test_get_product_not_found():
    response = client.get("/products/invalid-id")
    assert response.status_code == 404

def test_delete_product():
    create = client.post("/products", json={
        "name": "Tablet", "price": 299.99,
        "stock": 3, "category": "Electronics"
    })
    product_id = create.json()["product"]["id"]
    response = client.delete(f"/products/{product_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted!"

def test_delete_product_not_found():
    response = client.delete("/products/invalid-id")
    assert response.status_code == 404

# ── Users ───────────────────────────────────────────
def test_get_users_empty():
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_create_user():
    response = client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    })
    assert response.status_code == 201
    assert response.json()["user"]["name"] == "Prabu"

def test_get_user_by_id():
    create = client.post("/users", json={
        "name": "Kumar", "email": "kumar@example.com"
    })
    user_id = create.json()["user"]["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Kumar"

def test_create_duplicate_email():
    client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    })
    response = client.post("/users", json={
        "name": "Prabu2", "email": "prabu@example.com"
    })
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]

def test_get_user_not_found():
    response = client.get("/users/invalid-id")
    assert response.status_code == 404

def test_delete_user():
    create = client.post("/users", json={
        "name": "Test", "email": "test@example.com"
    })
    user_id = create.json()["user"]["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200

# ── Orders ──────────────────────────────────────────
def test_get_orders_empty():
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json()["total"] == 0

def test_create_order():
    user = client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    }).json()["user"]
    product = client.post("/products", json={
        "name": "Laptop", "price": 999.99,
        "stock": 10, "category": "Electronics"
    }).json()["product"]
    response = client.post("/orders", json={
        "user_id": user["id"],
        "product_id": product["id"],
        "quantity": 2
    })
    assert response.status_code == 201
    assert response.json()["order"]["total_price"] == 1999.98
    assert response.json()["order"]["status"] == "confirmed"

def test_create_order_insufficient_stock():
    user = client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    }).json()["user"]
    product = client.post("/products", json={
        "name": "Laptop", "price": 999.99,
        "stock": 1, "category": "Electronics"
    }).json()["product"]
    response = client.post("/orders", json={
        "user_id": user["id"],
        "product_id": product["id"],
        "quantity": 5
    })
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

def test_create_order_user_not_found():
    product = client.post("/products", json={
        "name": "Laptop", "price": 999.99,
        "stock": 10, "category": "Electronics"
    }).json()["product"]
    response = client.post("/orders", json={
        "user_id": "invalid-user",
        "product_id": product["id"],
        "quantity": 1
    })
    assert response.status_code == 404

def test_create_order_product_not_found():
    user = client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    }).json()["user"]
    response = client.post("/orders", json={
        "user_id": user["id"],
        "product_id": "invalid-product",
        "quantity": 1
    })
    assert response.status_code == 404

def test_get_order_by_id():
    user = client.post("/users", json={
        "name": "Prabu", "email": "prabu@example.com"
    }).json()["user"]
    product = client.post("/products", json={
        "name": "Phone", "price": 499.99,
        "stock": 5, "category": "Electronics"
    }).json()["product"]
    order = client.post("/orders", json={
        "user_id": user["id"],
        "product_id": product["id"],
        "quantity": 1
    }).json()["order"]
    response = client.get(f"/orders/{order['id']}")
    assert response.status_code == 200

def test_get_order_not_found():
    response = client.get("/orders/invalid-id")
    assert response.status_code == 404
