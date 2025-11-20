"""
Database Schemas for Jefferson Bar & Grill

Each Pydantic model represents a collection in your MongoDB database.
Collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# -----------------------------
# Public site content schemas
# -----------------------------

class Testimonial(BaseModel):
    author: str = Field(..., description="Person who gave the testimonial")
    quote: str = Field(..., description="Testimonial text")
    rating: Optional[int] = Field(5, ge=1, le=5)
    source: Optional[str] = Field(None, description="Where the quote came from (Google, Facebook, etc.)")

class Event(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    location: str = "The Jefferson Bar & Grill"
    is_holiday_special: bool = False
    image_url: Optional[str] = None

class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str = Field(..., description="e.g., Starters, Mains, Grills, Cocktails, Beer")
    is_seasonal: bool = False
    tags: List[str] = []

class GalleryItem(BaseModel):
    title: str
    image_url: str
    category: Optional[str] = Field(None, description="interior, exterior, food, people, holiday")

class Inquiry(BaseModel):
    name: str
    email: EmailStr
    message: str
    phone: Optional[str] = None
    source: str = "website"

# Note: The Flames database viewer will automatically use these schemas for validation.
