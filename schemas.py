"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    is_active: bool = Field(True, description="Whether user is active")


class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    category: str
    subcategory: Optional[str] = None
    image: Optional[str] = None
    in_stock: bool = True


class Review(BaseModel):
    name: str
    rating: int = Field(..., ge=1, le=5)
    comment: str
    source: Optional[str] = Field("website", description="Where the review was submitted")


class Consultation(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    mode: str = Field(..., description="in-person or online")
    preferred_date: Optional[str] = None
    message: Optional[str] = None
    service: str = Field("ayurvedic", description="ayurvedic or nakshatra")


class ContactMessage(BaseModel):
    full_name: str
    email: EmailStr
    topic: str
    message: str
    channel: Optional[str] = Field("general")


class BlogPost(BaseModel):
    title: str
    slug: str
    category: str
    excerpt: str
    content: str
    cover_image: Optional[str] = None
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None
