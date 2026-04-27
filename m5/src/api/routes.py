import json
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from src.cache.in_memory_cache import cache
from src.models.schemas import (
    CacheStats,
    HealthResponse,
    PaginatedResponse,
    Product,
    ProductCreate,
    ProductUpdate,
)
from src.services.product_service import product_service
from src.utils.helpers import format_timestamp
from config.settings import APP_VERSION

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        timestamp=format_timestamp(),
        version=APP_VERSION,
        cache_stats=cache.get_stats(),
    )


@router.get("/products", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
):
    cache_key = f"products:list:{page}:{page_size}:{category}:{search}"
    cached = cache.get(cache_key)
    if cached is not None:
        return PaginatedResponse(**cached)
    result = product_service.get_all(page, page_size, category, search)
    cache.set(cache_key, result.model_dump())
    return result


@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: int):
    cache_key = f"products:item:{product_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return Product(**cached)
    product = product_service.get_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    cache.set(cache_key, product.model_dump())
    return product


@router.post("/products", response_model=Product, status_code=201)
async def create_product(data: ProductCreate):
    product = product_service.create(data)
    # Invalidate all list caches since a new item was added
    cache.invalidate_pattern("products:list:")
    return product


@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: int, data: ProductUpdate):
    product = product_service.update(product_id, data)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    cache.delete(f"products:item:{product_id}")
    cache.invalidate_pattern("products:list:")
    return product


@router.delete("/products/{product_id}", status_code=204)
async def delete_product(product_id: int):
    deleted = product_service.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    cache.delete(f"products:item:{product_id}")
    cache.invalidate_pattern("products:list:")


@router.get("/categories")
async def list_categories():
    cache_key = "categories:all"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    categories = product_service.get_categories()
    cache.set(cache_key, categories)
    return categories


@router.get("/cache/stats", response_model=CacheStats)
async def cache_stats():
    stats = cache.get_stats()
    return CacheStats(**stats)


@router.delete("/cache", status_code=204)
async def clear_cache():
    cache.clear()
