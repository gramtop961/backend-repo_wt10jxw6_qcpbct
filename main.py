import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

from database import db, create_document, get_documents
from schemas import Product, Review, Consultation, ContactMessage, BlogPost

app = FastAPI(title="Ayurvedic Pharmacy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Ayurvedic Pharmacy API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ----- Helpers -----
AYURVEDIC_SUBCATEGORIES = [
    "Cosmetics", "Oils", "Balms", "Arishta & Asava", "Kwatha & Kashaya", "Powders", "Capsules & Tablets"
]
DISEASE_SUBCATEGORIES = [
    "Joint & Muscle Pain", "Digestive Disorders", "Respiratory Health", "Skin Conditions", "Women's Health",
    "Stress & Sleep", "Diabetes Support", "Immunity Boosters", "Hair & Scalp Problems"
]
TRADITIONAL_SUBCATEGORIES = [
    "Puja Items", "Pottery Items", "Thovil Badu", "Gift Packs/Herbal Kits"
]

PRODUCT_CATEGORIES = {
    "Ayurvedic Products": AYURVEDIC_SUBCATEGORIES,
    "Disease-Related Products": DISEASE_SUBCATEGORIES,
    "Traditional Products": TRADITIONAL_SUBCATEGORIES,
}


def ensure_seed_data():
    """Seed minimal placeholder documents if collections are empty."""
    try:
        # Products
        if db["product"].count_documents({}) == 0:
            samples: List[Product] = [
                Product(title="Neem Herbal Oil", description="Cold-pressed neem oil for skin and scalp.", price=12.99, category="Ayurvedic Products", subcategory="Oils", image=None),
                Product(title="Ashwagandha Capsules", description="Stress relief and vitality support.", price=18.5, category="Ayurvedic Products", subcategory="Capsules & Tablets", image=None),
                Product(title="DigestEase Arishta", description="Supports digestive comfort.", price=14.0, category="Ayurvedic Products", subcategory="Arishta & Asava", image=None),
                Product(title="Copper Puja Kalash", description="Traditional copper pot for rituals.", price=24.0, category="Traditional Products", subcategory="Puja Items", image=None),
                Product(title="Joint Relief Balm", description="Warming balm for joints and muscles.", price=7.5, category="Disease-Related Products", subcategory="Joint & Muscle Pain", image=None),
            ]
            for p in samples:
                create_document("product", p)
        # Reviews
        if db["review"].count_documents({}) == 0:
            sample_reviews: List[Review] = [
                Review(name="Anika", rating=5, comment="Amazing quality and very helpful staff!"),
                Review(name="Ravi", rating=4, comment="Consultation was insightful and products worked well."),
            ]
            for r in sample_reviews:
                create_document("review", r)
        # Blog
        if db["blogpost"].count_documents({}) == 0:
            sample_posts: List[BlogPost] = [
                BlogPost(title="Herbal Wisdom: Neem", slug="herbal-wisdom-neem", category="Herbal Wisdom", excerpt="Discover the multifaceted benefits of Neem.", content="Long form content about Neem..."),
                BlogPost(title="Healing Through Ayurveda: Digestive Balance", slug="healing-ayurveda-digestive", category="Healing Through Ayurveda", excerpt="Rekindle your digestive fire.", content="Content on Agni and digestion..."),
                BlogPost(title="Power of Nature: Ashwagandha", slug="power-of-nature-ashwagandha", category="Power of Nature", excerpt="Ashwagandha for stress relief.", content="Content about adaptogens..."),
                BlogPost(title="Ayurveda for Daily Life: Morning Rituals", slug="ayurveda-daily-life-morning", category="Ayurveda for Daily Life", excerpt="Simple practices to start your day.", content="Dinacharya overview..."),
            ]
            for b in sample_posts:
                create_document("blogpost", b)
    except Exception:
        # If seeding fails (e.g., DB not configured), ignore silently
        pass


@app.on_event("startup")
async def on_startup():
    ensure_seed_data()


# ----- Products -----
class ProductQuery(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None


@app.get("/api/categories")
def get_categories():
    return PRODUCT_CATEGORIES


@app.get("/api/products")
def list_products(q: Optional[str] = None, category: Optional[str] = None, subcategory: Optional[str] = None):
    ensure_seed_data()
    try:
        filt = {}
        if category:
            filt["category"] = category
        if subcategory:
            filt["subcategory"] = subcategory
        if q:
            # Basic text search using regex
            filt["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
            ]
        items = get_documents("product", filt)
        # Convert ObjectId to string
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/products")
def create_product(product: Product):
    try:
        _id = create_document("product", product)
        return {"_id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Reviews -----
@app.get("/api/reviews")
def get_reviews(limit: int = 50):
    try:
        reviews = get_documents("review", {}, limit=limit)
        for r in reviews:
            r["_id"] = str(r.get("_id"))
        return reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reviews")
def add_review(review: Review):
    try:
        _id = create_document("review", review)
        return {"_id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Blog -----
BLOG_CATEGORIES = [
    "Herbal Wisdom",
    "Healing Through Ayurveda",
    "Power of Nature",
    "Ayurveda for Daily Life",
]


@app.get("/api/blog")
def list_blog(category: Optional[str] = None):
    ensure_seed_data()
    try:
        filt = {"category": category} if category else {}
        posts = get_documents("blogpost", filt)
        for p in posts:
            p["_id"] = str(p.get("_id"))
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/blog")
def create_blog(post: BlogPost):
    try:
        if not post.published_at:
            post.published_at = datetime.utcnow()
        _id = create_document("blogpost", post)
        return {"_id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----- Services & Forms -----
SERVICES_INFO = {
    "ayurvedic": {
        "title": "Ayurvedic Consultations",
        "items": [
            "Doctor consultations (in-person/online)",
            "Prescription-based product supply",
        ],
    },
    "nakshatra": {
        "title": "Nakshatra Services",
        "items": [
            "Personal horoscope reading",
            "Wedding/event calculations",
            "Healing rituals",
            "Newborn name selection",
            "Auspicious time calculation",
            "Customized ritual items",
        ],
    },
}


@app.get("/api/services")
def get_services():
    return SERVICES_INFO


@app.post("/api/consultations")
def book_consultation(data: Consultation):
    try:
        _id = create_document("consultation", data)
        return {"_id": _id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/contact")
def contact(data: ContactMessage):
    try:
        _id = create_document("contactmessage", data)
        return {"_id": _id, "status": "received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
