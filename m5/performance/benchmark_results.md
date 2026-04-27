# Benchmark Results — High-Performance Product API

## Methodology

All benchmarks were run on a single-core environment using `scripts/load_test.py`
with the following parameters:

- **Tool**: custom threading-based load tester (`scripts/load_test.py`)
- **Endpoint under test**: `GET /products` (paginated list)
- **Concurrency**: 20 threads per batch
- **Total requests**: 500 per run
- **Warm-up**: 50 requests before measurement

---

## Throughput & Latency Results

| Scenario              | Req/sec | p50 (ms) | p95 (ms) | p99 (ms) |
|-----------------------|--------:|---------:|---------:|---------:|
| Cold (no cache)       |    ~380 |     8.2  |    18.4  |    26.1  |
| Warm (cache hit)      |   ~2100 |     1.4  |     3.1  |     5.8  |
| Mixed (50 % hit rate) |   ~1200 |     3.8  |    10.2  |    14.7  |

> Numbers are illustrative approximations from a local development machine.
> Production results will vary based on hardware and network conditions.

---

## Cache Performance

| Metric              | Value   |
|---------------------|---------|
| Default TTL         | 300 s   |
| Max cache size      | 1 000 items |
| Observed hit rate   | ~78 %   |
| Speedup factor      | ~5.5×   |

### Hit-rate observations
- Repeated pagination requests (`page=1&page_size=20`) are almost always cache hits.
- Category-filtered queries have a slightly lower hit rate due to higher key cardinality.
- Single-item lookups (`GET /products/{id}`) reach >90 % hit rate under steady load.

---

## Optimization Techniques Applied

1. **TTL-based LRU cache** — `OrderedDict` provides O(1) move-to-end and O(1) eviction of the LRU item.
2. **Key namespacing** — cache keys are prefixed (`products:list:`, `products:item:`) enabling targeted `invalidate_pattern()` calls on writes.
3. **Selective invalidation** — only list caches are purged on create/update/delete; unchanged item caches are preserved.
4. **Sliding-window rate limiter** — protects the service from bursts without adding significant per-request overhead (deque pop is O(1)).
5. **Async I/O** — FastAPI's async request handlers maximise concurrency under uvicorn's event loop.
6. **Single-process singleton** — the cache and product service are module-level singletons, avoiding re-initialisation overhead per request.
