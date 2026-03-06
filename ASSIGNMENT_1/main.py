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