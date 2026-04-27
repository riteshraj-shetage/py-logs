"""Tests for the TTLCache implementation."""
import threading
import time

from src.cache.in_memory_cache import TTLCache


def test_set_and_get():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("foo", "bar")
    assert c.get("foo") == "bar"


def test_ttl_expiry():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("key", "value", ttl=1)
    assert c.get("key") == "value"
    time.sleep(1.1)
    assert c.get("key") is None


def test_lru_eviction():
    c = TTLCache(max_size=3, default_ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.set("c", 3)
    # Access 'a' so 'b' becomes LRU
    c.get("a")
    c.set("d", 4)  # should evict 'b'
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3
    assert c.get("d") == 4


def test_cache_stats():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("x", 10)
    c.get("x")        # hit
    c.get("x")        # hit
    c.get("missing")  # miss
    stats = c.get_stats()
    assert stats["hits"] == 2
    assert stats["misses"] == 1
    assert stats["size"] == 1
    assert stats["hit_rate"] == round(2 / 3, 4)


def test_invalidate_pattern():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("products:list:1", "data1")
    c.set("products:list:2", "data2")
    c.set("products:item:1", "item1")
    removed = c.invalidate_pattern("products:list:")
    assert removed == 2
    assert c.get("products:list:1") is None
    assert c.get("products:list:2") is None
    assert c.get("products:item:1") == "item1"


def test_delete():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("k", "v")
    assert c.delete("k") is True
    assert c.get("k") is None
    assert c.delete("k") is False


def test_clear():
    c = TTLCache(max_size=100, default_ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.clear()
    assert c.get("a") is None
    assert c.get_stats()["size"] == 0


def test_thread_safety():
    c = TTLCache(max_size=500, default_ttl=60)
    errors = []

    def worker(thread_id: int):
        try:
            for i in range(50):
                key = f"thread:{thread_id}:key:{i}"
                c.set(key, i)
                val = c.get(key)
                assert val == i or val is None  # may have been evicted
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert errors == [], f"Thread safety errors: {errors}"
