from fastapi import FastAPI, HTTPException
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Product list
products = [

    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

# Show all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# Filter products by price
@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None
):

    result = products

    if category:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return {
        "products": result,
        "total": len(result)
    }


# Get only price of product
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}


# Filter by category
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [
        p for p in products
        if p["category"].lower() == category_name.lower()
    ]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


# Show only in stock
@app.get("/products/instock")
def get_instock():

    available = [
        p for p in products
        if p["in_stock"]
    ]

    return {
        "in_stock_products": available,
        "count": len(available)
    }


# Store summary
@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }


# Search products
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
    ]

    if not results:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }


# Cheapest and most expensive product
@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }


# Feedback storage
feedback = []


# Feedback model
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)


# Submit feedback
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

orders = []
order_counter = 1

class OrderItem(BaseModel):
    product_id: int
    quantity: int


class BulkOrder(BaseModel):
    orders: list[OrderItem]


class ConfirmOrder(BaseModel):
    order_id: int



@app.post("/orders/bulk")
def create_bulk_orders(data: BulkOrder):

    global order_counter

    confirmed = []
    failed = []
    grand_total = 0

    for item in data.orders:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if product is None:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if product["in_stock"] is False:
            failed.append({
                "product_id": item.product_id,
                "reason": "Out of stock"
            })
            continue

        total_price = product["price"] * item.quantity
        grand_total += total_price

        order = {
            "order_id": order_counter,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "status": "pending"
        }

        orders.append(order)
        confirmed.append(order)

        order_counter += 1

    return {
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

@app.patch("/confirm")
def confirm_order(data: ConfirmOrder):

    for order in orders:
        if order["order_id"] == data.order_id:
            order["status"] = "confirmed"
            return {
                "message": "Order confirmed",
                "order": order
            }

    return {"error": "Order not found"}


# Product model for POST
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool



# ADD PRODUCT (Q1)
@app.post("/products", status_code=201)
def add_product(product: Product):

    for p in products:
        if p["name"].lower() == product.name.lower():
            raise HTTPException(status_code=400, detail="Product already exists")

    new_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }



# DISCOUNT ENDPOINT (BONUS)
# must be above /products/{id}

@app.put("/products/discount")
def discount_products(category: str, discount_percent: int):

    if discount_percent < 1 or discount_percent > 99:
        raise HTTPException(status_code=400, detail="Discount must be between 1-99")

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price
            updated.append({"name": p["name"], "new_price": new_price})

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated),
        "products": updated
    }



# INVENTORY AUDIT (Q5)
@app.get("/products/audit")
def audit_products():

    total_products = len(products)

    in_stock_products = [p for p in products if p["in_stock"]]
    in_stock_count = len(in_stock_products)

    out_of_stock = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_products)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# UPDATE PRODUCT (Q2)-
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for p in products:
        if p["id"] == product_id:

            if price is not None:
                p["price"] = price

            if in_stock is not None:
                p["in_stock"] = in_stock

            return {
                "message": "Product updated",
                "product": p
            }

    raise HTTPException(status_code=404, detail="Product not found")


# DELETE PRODUCT (Q3)
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for i, p in enumerate(products):
        if p["id"] == product_id:
            name = p["name"]
            del products[i]

            return {
                "message": f"Product '{name}' deleted"
            }

    raise HTTPException(status_code=404, detail="Product not found")



# Show all products
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }