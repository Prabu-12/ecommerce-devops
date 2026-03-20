from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(
    title="E-Commerce API",
    description="Real-world DevOps showcase project",
    version="1.0.0"
)

# ── In-memory storage ──────────────────────────────
products_db = {}
orders_db = {}
users_db = {}

# ── Models ─────────────────────────────────────────
class Product(BaseModel):
    """Product model."""
    name: str
    price: float
    stock: int
    category: str

class Order(BaseModel):
    """Order model."""
    user_id: str
    product_id: str
    quantity: int

class User(BaseModel):
    """User model."""
    name: str
    email: str

# ── Health & Root ───────────────────────────────────
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "app": "E-Commerce API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/products", "/orders", "/users", "/health"]
    }

@app.get("/health")
def health():
    """Health check endpoint."""
    return {
        "status": "UP",
        "products": len(products_db),
        "orders": len(orders_db),
        "users": len(users_db)
    }

# ── Products ────────────────────────────────────────
@app.get("/products")
def get_products():
    """Get all products."""
    return {"products": list(products_db.values()), "total": len(products_db)}

@app.get("/products/{product_id}")
def get_product(product_id: str):
    """Get product by ID."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]

@app.post("/products", status_code=201)
def create_product(product: Product):
    """Create a new product."""
    product_id = str(uuid.uuid4())
    products_db[product_id] = {
        "id": product_id,
        "name": product.name,
        "price": product.price,
        "stock": product.stock,
        "category": product.category
    }
    return {"message": "Product created!", "product": products_db[product_id]}

@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    """Delete a product."""
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    deleted = products_db.pop(product_id)
    return {"message": "Product deleted!", "product": deleted}

# ── Orders ──────────────────────────────────────────
@app.get("/orders")
def get_orders():
    """Get all orders."""
    return {"orders": list(orders_db.values()), "total": len(orders_db)}

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    """Get order by ID."""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id]

@app.post("/orders", status_code=201)
def create_order(order: Order):
    """Create a new order."""
    if order.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    if order.product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    product = products_db[order.product_id]
    if product["stock"] < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    order_id = str(uuid.uuid4())
    total_price = product["price"] * order.quantity
    products_db[order.product_id]["stock"] -= order.quantity
    orders_db[order_id] = {
        "id": order_id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "total_price": total_price,
        "status": "confirmed"
    }
    return {"message": "Order created!", "order": orders_db[order_id]}

# ── Users ───────────────────────────────────────────
@app.get("/users")
def get_users():
    """Get all users."""
    return {"users": list(users_db.values()), "total": len(users_db)}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    """Get user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.post("/users", status_code=201)
def create_user(user: User):
    """Create a new user."""
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    user_id = str(uuid.uuid4())
    users_db[user_id] = {
        "id": user_id,
        "name": user.name,
        "email": user.email
    }
    return {"message": "User created!", "user": users_db[user_id]}

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    deleted = users_db.pop(user_id)
    return {"message": "User deleted!", "user": deleted}
