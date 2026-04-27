import random
from datetime import datetime, timezone
from typing import List

from src.models.schemas import Product

CATEGORIES = [
    "Electronics", "Books", "Clothing", "Home & Garden", "Sports",
    "Toys", "Automotive", "Health", "Beauty", "Food & Grocery",
]

ADJECTIVES = [
    "Premium", "Ultra", "Pro", "Smart", "Classic", "Deluxe",
    "Advanced", "Essential", "Elite", "Super",
]

NOUNS = [
    "Widget", "Gadget", "Device", "Tool", "Kit", "Set",
    "Module", "Unit", "System", "Pack",
]


def generate_products(n: int, seed: int = 42) -> List[Product]:
    """Generate n sample products with realistic names/categories/prices."""
    rng = random.Random(seed)
    products = []
    for i in range(1, n + 1):
        adj = rng.choice(ADJECTIVES)
        noun = rng.choice(NOUNS)
        category = rng.choice(CATEGORIES)
        price = round(rng.uniform(1.99, 999.99), 2)
        stock = rng.randint(0, 500)
        products.append(
            Product(
                id=i,
                name=f"{adj} {noun} {i}",
                category=category,
                price=price,
                stock=stock,
                description=f"High-quality {adj.lower()} {noun.lower()} for {category.lower()} enthusiasts.",
                created_at=format_timestamp(),
            )
        )
    return products


def paginate(items: list, page: int, page_size: int) -> dict:
    """Return a slice of items for the requested page."""
    total = len(items)
    pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, pages))
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }


def format_timestamp() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
