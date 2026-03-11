from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import FastAPI

app = FastAPI()

# Product data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 120, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": False},
    {"id": 4, "name": "USB Cable", "price": 199, "category": "Electronics", "in_stock": True},

    # Added products
    {"id": 5, "name": "Laptop Stand", "price": 899, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1299, "category": "Electronics", "in_stock": False}
]




@app.get("/")
def home():
    return {"message": "Store API is running"}


# Q1 - Show all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# Q2 - Filter by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    result = []
    for p in products:
        if p["category"].lower() == category_name.lower():
            result.append(p)

    if len(result) == 0:
        return {"error": "No products found in this category"}

    return {"products": result, "count": len(result)}


# Q3 - Only in-stock products
@app.get("/products/instock")
def get_instock_products():

    instock = []
    for p in products:
        if p["in_stock"]:
            instock.append(p)

    return {
        "in_stock_products": instock,
        "count": len(instock)
    }


# Q4 - Store summary
@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = 0
    for p in products:
        if p["in_stock"]:
            in_stock += 1

    out_of_stock = total_products - in_stock

    categories = []
    for p in products:
        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_of_stock,
        "categories": categories
    }


# Q5 - Search products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    matches = []
    for p in products:
        if keyword.lower() in p["name"].lower():
            matches.append(p)

    if len(matches) == 0:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matches,
        "count": len(matches)
    }


# Bonus question- Cheapest and most expensive
@app.get("/products/deals")
def product_deals():

    cheapest = products[0]
    expensive = products[0]

    for p in products:
        if p["price"] < cheapest["price"]:
            cheapest = p
        if p["price"] > expensive["price"]:
            expensive = p

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }
    
from typing import Optional, List
from pydantic import BaseModel, Field

# Storage lists
feedback = []
orders = []


# Q1 - Filter products with query parameters
@app.get("/products/filter")
def filter_products(min_price: Optional[int] = None, max_price: Optional[int] = None, category: Optional[str] = None):

    result = []

    for p in products:

        if min_price is not None and p["price"] < min_price:
            continue

        if max_price is not None and p["price"] > max_price:
            continue

        if category is not None and p["category"].lower() != category.lower():
            continue

        result.append(p)

    return {"products": result, "count": len(result)}


# Q2 - Return only product name and price
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for p in products:
        if p["id"] == product_id:
            return {
                "name": p["name"],
                "price": p["price"]
            }

    return {"error": "Product not found"}


# Q3 - Customer feedback model
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


# Q3 - POST feedback endpoint
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data.dict())

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }


# Q4 - Product summary dashboard
@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock = 0
    for p in products:
        if p["in_stock"]:
            in_stock += 1

    out_of_stock = total_products - in_stock

    cheapest = products[0]
    expensive = products[0]

    for p in products:

        if p["price"] < cheapest["price"]:
            cheapest = p

        if p["price"] > expensive["price"]:
            expensive = p

    categories = []

    for p in products:
        if p["category"] not in categories:
            categories.append(p["category"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock,
        "out_of_stock_count": out_of_stock,
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }


# Q5 - Order item model
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)


# Q5 - Bulk order model
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]


# Q5 - Bulk order endpoint
@app.post("/orders/bulk")
def bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = None

        for p in products:
            if p["id"] == item.product_id:
                product = p
                break

        if product is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }


# BONUS - Create order (pending)
@app.post("/orders")
def create_order(product_id: int):

    order_id = len(orders) + 1

    order = {
        "id": order_id,
        "product_id": product_id,
        "status": "pending"
    }

    orders.append(order)

    return order


# BONUS - Get order
@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for o in orders:
        if o["id"] == order_id:
            return o

    return {"error": "Order not found"}


# BONUS - Confirm order
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for o in orders:
        if o["id"] == order_id:
            o["status"] = "confirmed"
            return o
