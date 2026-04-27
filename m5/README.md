# High-Performance Web Service — Option 1 (m5)

FastAPI service with TTL in-process LRU cache and per-IP rate limiting.

---

## Project Structure

```
complete-tasks/m5/
├── README.md
├── requirements.txt
├── config/
│   └── settings.py          # Centralised configuration
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── api/routes.py        # All route handlers
│   ├── services/product_service.py
│   ├── models/schemas.py    # Pydantic v2 models
│   ├── cache/in_memory_cache.py  # TTL-based LRU cache
│   ├── middleware/rate_limiter.py
│   └── utils/helpers.py
├── tests/
│   ├── test_api.py
│   └── test_cache.py
├── performance/
│   └── benchmark_results.md
├── docs/
│   └── architecture.md
└── scripts/
    └── load_test.py
```

---

## Setup & Run

```bash
cd complete-tasks/m5
pip install -r requirements.txt
uvicorn src.main:app --reload
```

The API is then available at `http://localhost:8000`.

Interactive docs: `http://localhost:8000/docs`

---

## API Endpoints

| Method   | Path               | Description                                | Cached |
|----------|--------------------|---------------------------------------------|--------|
| GET      | `/health`          | Health check with cache statistics          | No     |
| GET      | `/products`        | Paginated list (+ `category`, `search`)     | Yes    |
| GET      | `/products/{id}`   | Single product by ID                        | Yes    |
| POST     | `/products`        | Create a new product                        | —      |
| PUT      | `/products/{id}`   | Update a product (partial)                  | —      |
| DELETE   | `/products/{id}`   | Delete a product                            | —      |
| GET      | `/categories`      | List all unique categories                  | Yes    |
| GET      | `/cache/stats`     | Cache hit/miss statistics                   | No     |
| DELETE   | `/cache`           | Clear the entire cache                      | —      |

### Query Parameters — `GET /products`

| Param       | Type    | Default | Description              |
|-------------|---------|---------|--------------------------|
| `page`      | int     | 1       | Page number (≥ 1)        |
| `page_size` | int     | 20      | Items per page (1–100)   |
| `category`  | string  | —       | Filter by category name  |
| `search`    | string  | —       | Search in name/description |

---

## Performance Notes

### Caching Strategy
- **Algorithm**: Cache-Aside (Lazy Loading)
- **Implementation**: `TTLCache` — `OrderedDict`-backed LRU with per-entry TTL
- **Default TTL**: 300 seconds (configurable in `config/settings.py`)
- **Max size**: 1 000 items (LRU eviction when full)
- **Write invalidation**: List caches purged on any write; item caches targeted by key

### Rate Limiting
- **Algorithm**: Sliding window counter per client IP
- **Limit**: 100 requests / 60-second window (configurable)
- **Response on breach**: HTTP 429 with `Retry-After` header
- **Exempt**: `/health` endpoint

### Benchmark Summary

| Scenario         | Req/sec | p50   | p95   |
|------------------|--------:|------:|------:|
| Cold (no cache)  | ~380    | 8 ms  | 18 ms |
| Warm (cache hit) | ~2100   | 1.4ms | 3 ms  |

See `performance/benchmark_results.md` for full details.

---

## Running Tests

```bash
cd complete-tasks/m5
python -m pytest tests/ -v
```

---

## Architecture Highlights

- **FastAPI + uvicorn** — async ASGI stack for high concurrency
- **TTLCache singleton** — shared in-process cache, zero network overhead
- **Key namespacing** — prefixed cache keys enable bulk `invalidate_pattern()` on writes
- **RateLimitMiddleware** — Starlette middleware, runs before routing
- **Pydantic v2** — fast schema validation and serialisation
- **Deterministic seed** — 500 sample products generated with `random.Random(seed=42)`

See `docs/architecture.md` for the full architecture document.
