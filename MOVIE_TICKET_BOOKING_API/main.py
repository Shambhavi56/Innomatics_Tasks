import math
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="CineStar Booking API")

# ==========================================
# DATA
# ==========================================
movies = [
    {"id": 1, "title": "The Quantum Paradox", "genre": "Action", "language": "English", "duration_mins": 120, "ticket_price": 15, "seats_available": 100},
    {"id": 2, "title": "Laugh Out Loud", "genre": "Comedy", "language": "Spanish", "duration_mins": 95, "ticket_price": 12, "seats_available": 50},
    {"id": 3, "title": "Tears in the Rain", "genre": "Drama", "language": "English", "duration_mins": 140, "ticket_price": 14, "seats_available": 80},
    {"id": 4, "title": "Nightmare Manor", "genre": "Horror", "language": "English", "duration_mins": 105, "ticket_price": 13, "seats_available": 60},
    {"id": 5, "title": "Explosion Protocol", "genre": "Action", "language": "French", "duration_mins": 110, "ticket_price": 16, "seats_available": 120},
    {"id": 6, "title": "Romantic Comedy 101", "genre": "Comedy", "language": "English", "duration_mins": 100, "ticket_price": 10, "seats_available": 40},
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# ==========================================
# MODELS
# ==========================================
class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

class SeatHoldRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)

# ==========================================
# HELPERS
# ==========================================
def find_movie(movie_id: int):
    return next((m for m in movies if m["id"] == movie_id), None)

def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    multiplier = 1
    if seat_type.lower() == "premium":
        multiplier = 1.5
    elif seat_type.lower() == "recliner":
        multiplier = 2

    original = base_price * seats * multiplier

    discount = 0
    if promo_code.upper() == "SAVE10":
        discount = 0.10
    elif promo_code.upper() == "SAVE20":
        discount = 0.20

    final = original * (1 - discount)

    return original, final

def filter_movies_logic(genre=None, language=None, max_price=None, min_seats=None):
    result = movies
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]
    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]
    return result

# ==========================================
# ROOT
# ==========================================
@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# ==========================================
# MOVIES
# ==========================================
@app.get("/movies/summary")
def summary():
    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "cheapest": min(movies, key=lambda x: x["ticket_price"])["ticket_price"],
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_count": genre_count
    }

@app.get("/movies/filter")
def filter_movies(genre: Optional[str] = None, language: Optional[str] = None,
                  max_price: Optional[int] = None, min_seats: Optional[int] = None):
    data = filter_movies_logic(genre, language, max_price, min_seats)
    return {"total": len(data), "movies": data}

@app.get("/movies/search")
def search_movies(keyword: str):
    kw = keyword.lower()
    result = [m for m in movies if kw in (m["title"] + m["genre"] + m["language"]).lower()]
    if not result:
        return {"message": "No movies found", "total_found": 0}
    return {"total_found": len(result), "movies": result}

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    valid = ["ticket_price", "title", "duration_mins", "seats_available"]
    if sort_by not in valid:
        raise HTTPException(400, f"Invalid sort field. Choose from {valid}")
    return sorted(movies, key=lambda x: x[sort_by], reverse=(order == "desc"))

@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    total = len(movies)
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "total_pages": math.ceil(total / limit),
        "movies": movies[start:end]
    }

@app.get("/movies/browse")
def browse(keyword: str = None, genre: str = None, language: str = None,
           sort_by: str = "ticket_price", order: str = "asc",
           page: int = 1, limit: int = 3):

    result = movies

    if keyword:
        kw = keyword.lower()
        result = [m for m in result if kw in (m["title"] + m["genre"] + m["language"]).lower()]

    if genre:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language:
        result = [m for m in result if m["language"].lower() == language.lower()]

    valid = ["ticket_price", "title", "duration_mins", "seats_available"]
    if sort_by in valid:
        result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": len(result),
        "total_pages": math.ceil(len(result) / limit),
        "movies": result[start:end]
    }

@app.get("/movies")
def get_movies():
    return {
        "total": len(movies),
        "total_seats": sum(m["seats_available"] for m in movies),
        "movies": movies
    }

@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    if any(m["title"].lower() == movie.title.lower() for m in movies):
        raise HTTPException(400, "Duplicate title")
    new = movie.model_dump()
    new["id"] = max(m["id"] for m in movies) + 1
    movies.append(new)
    return new

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")
    return movie

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: int = None, seats_available: int = None):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")
    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available
    return movie

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")
    if any(b["movie_title"] == movie["title"] for b in bookings):
        raise HTTPException(400, "Cannot delete movie with bookings")
    movies.remove(movie)
    return {"message": "Deleted"}

# ==========================================
# BOOKINGS
# ==========================================
@app.get("/bookings")
def get_bookings():
    return {
        "total": len(bookings),
        "revenue": sum(b["total_cost"] for b in bookings),
        "bookings": bookings
    }

@app.get("/bookings/search")
def search_bookings(customer_name: str):
    kw = customer_name.lower()
    result = [b for b in bookings if kw in b["customer_name"].lower()]
    return {"total_found": len(result), "bookings": result}

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost", order: str = "desc"):
    valid = ["total_cost", "seats_booked"]
    if sort_by not in valid:
        raise HTTPException(400, f"Invalid sort field. Choose from {valid}")
    return sorted(bookings, key=lambda x: x[sort_by], reverse=(order == "desc"))

@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 3):
    total = len(bookings)
    start = (page - 1) * limit
    end = start + limit
    return {
        "total": total,
        "total_pages": math.ceil(total / limit),
        "bookings": bookings[start:end]
    }

@app.post("/bookings", status_code=201)
def create_booking(req: BookingRequest):
    global booking_counter

    movie = find_movie(req.movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < req.seats:
        raise HTTPException(400, "Not enough seats")

    original, final = calculate_ticket_cost(
        movie["ticket_price"], req.seats, req.seat_type, req.promo_code
    )

    movie["seats_available"] -= req.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": req.customer_name,
        "movie_title": movie["title"],
        "seats_booked": req.seats,
        "seat_type": req.seat_type,
        "original_cost": original,
        "total_cost": final
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ==========================================
# SEAT HOLD WORKFLOW
# ==========================================
@app.post("/seat-hold")
def hold(req: SeatHoldRequest):
    global hold_counter

    movie = find_movie(req.movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < req.seats:
        raise HTTPException(400, "Not enough seats")

    movie["seats_available"] -= req.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": req.customer_name,
        "movie_id": req.movie_id,
        "seats": req.seats
    }

    holds.append(hold)
    hold_counter += 1
    return hold

@app.get("/seat-hold")
def get_holds():
    return {"total_holds": len(holds), "holds": holds}

@app.post("/seat-confirm/{hold_id}")
def confirm(hold_id: int):
    global booking_counter

    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(404, "Hold not found")

    movie = find_movie(hold["movie_id"])

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie_title": movie["title"],
        "seats_booked": hold["seats"],
        "total_cost": hold["seats"] * movie["ticket_price"]
    }

    bookings.append(booking)
    holds.remove(hold)
    booking_counter += 1

    return booking

@app.delete("/seat-release/{hold_id}")
def release(hold_id: int):
    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(404, "Hold not found")

    movie = find_movie(hold["movie_id"])
    movie["seats_available"] += hold["seats"]

    holds.remove(hold)
    return {"message": "Hold released"}