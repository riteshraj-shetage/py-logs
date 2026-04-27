from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: int
    name: str
    category: str
    price: float
    stock: int
    description: str
    created_at: str


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str = Field(default="", max_length=1000)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    category: Optional[str] = Field(default=None, min_length=1, max_length=100)
    price: Optional[float] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    description: Optional[str] = Field(default=None, max_length=1000)


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class CacheStats(BaseModel):
    hits: int
    misses: int
    size: int
    hit_rate: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    cache_stats: dict


class ErrorResponse(BaseModel):
    error: str
    detail: str
    timestamp: str
