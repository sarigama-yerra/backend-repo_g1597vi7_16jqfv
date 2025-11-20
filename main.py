import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

from database import db, create_document, get_documents
from schemas import Testimonial, Event, MenuItem, GalleryItem, Inquiry

app = FastAPI(title="Jefferson Bar & Grill API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Jefferson Bar & Grill API running"}

@app.get("/test")
def test_database():
    """Test endpoint to check database connectivity and list collections"""
    status = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "collections": []
    }
    try:
        if db is not None:
            status["database"] = "✅ Connected"
            status["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            status["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                status["collections"] = db.list_collection_names()
            except Exception as e:
                status["database"] = f"⚠️ Connected but error listing collections: {str(e)[:80]}"
        else:
            status["database"] = "❌ Not Initialized"
    except Exception as e:
        status["database"] = f"❌ Error: {str(e)[:80]}"
    return status

# --------------------------------------
# Content seed helpers (non-endpoint)
# --------------------------------------

def seed_default_content():
    """Idempotent seed for initial content if collections are empty."""
    try:
        if db is None:
            return
        # Testimonials
        if db.testimonial.count_documents({}) == 0:
            testimonials = [
                {
                    "author": "Local Regular",
                    "quote": "Food was great, beer was affordable, and the vibe felt like home.",
                    "rating": 5,
                    "source": "Google"
                },
                {
                    "author": "First-time Visitor",
                    "quote": "Warm staff, great cocktails, and the neighborhood energy is real.",
                    "rating": 5,
                    "source": "Facebook"
                },
            ]
            for t in testimonials:
                create_document("testimonial", t)
        # Menu
        if db.menuitem.count_documents({}) == 0:
            menu_items = [
                {"name": "Smash Burger", "description": "Double patty, melted cheese, house sauce", "price": 12.0, "category": "Mains"},
                {"name": "Wings", "description": "Crispy wings, choice of sauces", "price": 11.0, "category": "Starters"},
                {"name": "House Old Fashioned", "description": "Bourbon, bitters, orange twist", "price": 10.0, "category": "Cocktails"},
                {"name": "Holiday Spiced Cider", "description": "Seasonal, warm and cozy", "price": 8.0, "category": "Cocktails", "is_seasonal": True},
            ]
            for m in menu_items:
                create_document("menuitem", m)
        # Events
        if db.event.count_documents({}) == 0:
            events = [
                {
                    "title": "Holiday Trivia Night",
                    "description": "Bring your crew for festive trivia and prizes.",
                    "start_time": datetime.utcnow() + timedelta(days=3),
                    "location": "The Jefferson Bar & Grill",
                    "is_holiday_special": True
                },
                {
                    "title": "Christmas Eve Dinner Specials",
                    "description": "Limited-run holiday plates and cocktails.",
                    "start_time": datetime.utcnow() + timedelta(days=7),
                    "location": "The Jefferson Bar & Grill",
                    "is_holiday_special": True
                },
            ]
            for e in events:
                create_document("event", e)
        # Gallery
        if db.galleryitem.count_documents({}) == 0:
            gallery = [
                {"title": "Warm Lit Bar", "image_url": "/images/bar-warm.jpg", "category": "interior"},
                {"title": "Holiday Lights", "image_url": "/images/holiday-lights.jpg", "category": "holiday"},
            ]
            for g in gallery:
                create_document("galleryitem", g)
    except Exception:
        # Non-fatal; seeding is best-effort
        pass

# Call seed on import
seed_default_content()

# --------------------------------------
# API Models for requests
# --------------------------------------

class InquiryIn(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone: Optional[str] = None

# --------------------------------------
# API Endpoints
# --------------------------------------

@app.get("/api/testimonials", response_model=List[Testimonial])
def list_testimonials(limit: int = 10):
    docs = get_documents("testimonial", {}, limit)
    # Convert ObjectId and remove mongo fields
    for d in docs:
        d.pop("_id", None)
    return docs

@app.get("/api/menu", response_model=List[MenuItem])
def list_menu(category: Optional[str] = None, limit: int = 50):
    query = {"category": category} if category else {}
    docs = get_documents("menuitem", query, limit)
    for d in docs:
        d.pop("_id", None)
    return docs

@app.get("/api/events", response_model=List[Event])
def list_events(holiday_only: bool = False, limit: int = 20):
    query = {"is_holiday_special": True} if holiday_only else {}
    docs = get_documents("event", query, limit)
    for d in docs:
        d.pop("_id", None)
    return docs

@app.get("/api/gallery", response_model=List[GalleryItem])
def list_gallery(category: Optional[str] = None, limit: int = 20):
    query = {"category": category} if category else {}
    docs = get_documents("galleryitem", query, limit)
    for d in docs:
        d.pop("_id", None)
    return docs

@app.post("/api/inquiry")
def create_inquiry(payload: InquiryIn):
    try:
        create_document("inquiry", payload.model_dump())
        return {"ok": True, "message": "Thanks! We'll be in touch soon."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
