from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio

app = FastAPI(
    title="Limkokwing Library API",
    description="Library Management System for borrowing and returning books",
    version="1.0.0"
)

# -----------------------------
# In-Memory Database
# -----------------------------
books = [
    {
        "id": 1,
        "title": "Python Basics",
        "author": "John Doe",
        "category": "Programming",
        "available": True
    },
    {
        "id": 2,
        "title": "Database Systems",
        "author": "Jane Smith",
        "category": "ICT",
        "available": True
    },
    {
        "id": 3,
        "title": "Networking Essentials",
        "author": "David Cole",
        "category": "Networking",
        "available": True
    }
]

borrowed_books = []

# -----------------------------
# Models
# -----------------------------
class BorrowRequest(BaseModel):
    user_id: int
    book_id: int


class ReturnRequest(BaseModel):
    user_id: int
    book_id: int


# -----------------------------
# Routes
# -----------------------------

@app.get("/")
async def home():
    return {"message": "Welcome to Limkokwing Library API"}


@app.get("/books")
async def get_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    category: Optional[str] = None
):
    results = books

    if title:
        results = [b for b in results if title.lower() in b["title"].lower()]

    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]

    if category:
        results = [b for b in results if category.lower() in b["category"].lower()]

    return results


@app.post("/borrow")
async def borrow_book(data: BorrowRequest):
    await asyncio.sleep(1)

    for book in books:
        if book["id"] == data.book_id:

            if not book["available"]:
                raise HTTPException(
                    status_code=400,
                    detail="Book is already borrowed"
                )

            book["available"] = False

            borrowed_books.append({
                "user_id": data.user_id,
                "book_id": data.book_id,
                "borrow_date": datetime.now(),
                "due_date": datetime.now() + timedelta(days=7)
            })

            return {"message": "Book borrowed successfully"}

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/return")
async def return_book(data: ReturnRequest):
    await asyncio.sleep(1)

    for record in borrowed_books:
        if (
            record["user_id"] == data.user_id
            and record["book_id"] == data.book_id
        ):

            borrowed_books.remove(record)

            for book in books:
                if book["id"] == data.book_id:
                    book["available"] = True

            return {"message": "Book returned successfully"}

    raise HTTPException(status_code=404, detail="Borrow record not found")


@app.get("/overdue")
async def overdue_books():
    now = datetime.now()
    overdue_list = []

    for record in borrowed_books:
        if now > record["due_date"]:

            days_late = (now - record["due_date"]).days
            fine = days_late * 5

            overdue_list.append({
                "user_id": record["user_id"],
                "book_id": record["book_id"],
                "days_late": days_late,
                "fine": fine
            })

    return overdue_list