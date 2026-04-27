# Architecture — High-Performance Product API

## System Design Overview

```
Client
  │
  ▼
┌─────────────────────────────────────────────────────┐
│  uvicorn (ASGI server)                              │
│  ┌───────────────────────────────────────────────┐  │
│  │  FastAPI Application                          │  │
│  │                                               │  │
│  │  CORS Middleware                              │  │
│  │       ↓                                       │  │
│  │  RateLimitMiddleware (per-IP sliding window)  │  │
│  │       ↓                                       │  │
│  │  Router (API Routes)                          │  │
│  │    ├─ /health                                 │  │
│  │    ├─ /products      ◄──► TTLCache            │  │
│  │    ├─ /categories    ◄──► TTLCache            │  │
│  │    ├─ /cache/stats                            │  │
│  │    └─ /cache (DELETE)                         │  │
│  │       ↓                                       │  │
│  │  ProductService (in-memory dict DB)           │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## Component Descriptions

### `src/main.py`
Application entry point. Registers middleware, attaches the router, and sets up
lifecycle events (startup log, cache flush on shutdown) and a global exception handler.

### `src/api/routes.py`
All HTTP handlers. Cache-aside pattern is applied to read endpoints: check cache first,
fall through to the service on a miss, then populate the cache before returning.
Write operations (POST / PUT / DELETE) invalidate relevant cache keys.

### `src/services/product_service.py`
Business logic layer. Backed by a plain Python `dict` seeded with 500 products on startup
(deterministic via `random.Random(seed=42)`). Provides CRUD + filtering + pagination.

### `src/cache/in_memory_cache.py`
`TTLCache` — thread-safe, TTL-aware LRU cache using `collections.OrderedDict`.
Exposed as a module-level singleton (`cache`) imported by the routes layer.

### `src/middleware/rate_limiter.py`
`RateLimitMiddleware` — Starlette `BaseHTTPMiddleware` subclass that maintains a per-IP
`deque` of request timestamps. A sliding window of `RATE_LIMIT_WINDOW` seconds is used.
Returns HTTP 429 with a `Retry-After` header when the limit is exceeded.

### `config/settings.py`
Centralised configuration. All tuneable parameters (TTL, cache size, rate limits, port)
live here so they can be replaced by environment-variable reads in production.

---

## Caching Strategy

**Pattern**: Cache-Aside (Lazy Loading)

1. Route handler checks `TTLCache` for the request's cache key.
2. On a **hit** — return the cached value immediately (no service call).
3. On a **miss** — call the service, store the result, return to the client.
4. On a **write** — invalidate affected keys using `invalidate_pattern()` (list caches)
   or `delete()` (single-item cache).

**Key schema**:

| Key pattern                             | Cached data                  |
|-----------------------------------------|------------------------------|
| `products:list:{page}:{size}:{cat}:{q}` | Paginated product list       |
| `products:item:{id}`                    | Single product               |
| `categories:all`                        | List of all category strings |

---

## Rate Limiting Approach

- **Algorithm**: Sliding window counter per IP address.
- **Storage**: `defaultdict(deque)` — O(1) append and O(k) purge (k = expired entries).
- **Configuration**: `RATE_LIMIT_REQUESTS = 100` per `RATE_LIMIT_WINDOW = 60` seconds.
- **Exclusions**: `/health` is exempt to allow monitoring probes.
- **Response**: HTTP 429 with `Retry-After` header indicating seconds until the window resets.

---

## Scalability Considerations

### Horizontal Scaling
The current design is **single-process**. To scale horizontally:

1. **Replace `TTLCache` with Redis** — use `redis-py` or `aioredis` as a shared cache.
   The cache interface (`get`, `set`, `delete`, `invalidate_pattern`) maps directly to
   Redis commands (`GET`, `SET EX`, `DEL`, `SCAN` + `DEL`).

2. **Add a Load Balancer** — put Nginx or an AWS ALB in front of multiple uvicorn workers.
   Sticky sessions are not needed because Redis provides shared state.

3. **Rate limiter in Redis** — replace the in-process deque with an atomic Redis sorted-set
   counter (`ZADD` / `ZREMRANGEBYSCORE` / `ZCARD`) for cross-instance rate limiting.

4. **Database** — swap the in-memory dict for PostgreSQL (with asyncpg) or MongoDB.

### Vertical Scaling
- Run `uvicorn --workers N` (N = CPU cores) with the `gunicorn` process manager.
- Each worker gets its own `TTLCache`; consistency is maintained by short TTLs and
  write-through invalidation.

---

## Design Patterns Used

| Pattern           | Where                          | Purpose                                   |
|-------------------|--------------------------------|-------------------------------------------|
| **Singleton**     | `cache`, `product_service`     | One shared instance per process           |
| **Cache-Aside**   | Route handlers                 | Read from cache, fallback to service      |
| **Strategy**      | `RateLimitMiddleware`          | Pluggable rate-limiting algorithm         |
| **Repository**    | `ProductService`               | Abstracts data access from routes         |
| **Middleware**    | CORS, RateLimitMiddleware      | Cross-cutting concerns separate from logic|
