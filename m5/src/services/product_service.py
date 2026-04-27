from typing import Dict, List, Optional

from src.cache.in_memory_cache import cache
from src.models.schemas import PaginatedResponse, Product, ProductCreate, ProductUpdate
from src.utils.helpers import format_timestamp, generate_products, paginate
from config.settings import PRODUCTS_COUNT


class ProductService:
    """Service layer for product operations backed by an in-memory dict."""

    def __init__(self):
        products = generate_products(PRODUCTS_COUNT)
        self._db: Dict[int, Product] = {p.id: p for p in products}
        self._next_id = PRODUCTS_COUNT + 1

    def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse:
        items = list(self._db.values())
        if category:
            items = [p for p in items if p.category.lower() == category.lower()]
        if search:
            search_lower = search.lower()
            items = [
                p for p in items
                if search_lower in p.name.lower() or search_lower in p.description.lower()
            ]
        paginated = paginate(items, page, page_size)
        return PaginatedResponse(
            items=[p.model_dump() for p in paginated["items"]],
            total=paginated["total"],
            page=paginated["page"],
            page_size=paginated["page_size"],
            pages=paginated["pages"],
        )

    def get_by_id(self, product_id: int) -> Optional[Product]:
        return self._db.get(product_id)

    def create(self, data: ProductCreate) -> Product:
        product = Product(
            id=self._next_id,
            name=data.name,
            category=data.category,
            price=data.price,
            stock=data.stock,
            description=data.description,
            created_at=format_timestamp(),
        )
        self._db[product.id] = product
        self._next_id += 1
        return product

    def update(self, product_id: int, data: ProductUpdate) -> Optional[Product]:
        product = self._db.get(product_id)
        if product is None:
            return None
        updated = product.model_dump()
        patch = data.model_dump(exclude_none=True)
        updated.update(patch)
        self._db[product_id] = Product(**updated)
        return self._db[product_id]

    def delete(self, product_id: int) -> bool:
        if product_id in self._db:
            del self._db[product_id]
            return True
        return False

    def get_categories(self) -> List[str]:
        return sorted({p.category for p in self._db.values()})


# Module-level singleton
product_service = ProductService()
