"""Integration tests for the FastAPI routes."""
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.cache.in_memory_cache import cache


@pytest_asyncio.fixture(autouse=True)
async def clear_cache_between_tests():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "cache_stats" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_list_products():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 500
    assert len(data["items"]) == 20  # default page_size


@pytest.mark.asyncio
async def test_list_products_with_category_filter():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products?category=Electronics")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category"] == "Electronics"


@pytest.mark.asyncio
async def test_get_product_by_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "name" in data
    assert "price" in data


@pytest.mark.asyncio
async def test_get_product_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/products/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_product():
    payload = {
        "name": "Test Gadget",
        "category": "Electronics",
        "price": 49.99,
        "stock": 10,
        "description": "A test product.",
    }
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Gadget"
    assert data["id"] > 500


@pytest.mark.asyncio
async def test_update_product():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put("/products/1", json={"price": 9999.99})
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == 9999.99
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_delete_product():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        del_response = await client.delete("/products/2")
        assert del_response.status_code == 204
        get_response = await client.get("/products/2")
        assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_cache_stats():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get("/products/1")
        await client.get("/products/1")  # second call should be a cache hit
        response = await client.get("/cache/stats")
    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert data["hits"] >= 1


@pytest.mark.asyncio
async def test_pagination():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r1 = await client.get("/products?page=1&page_size=10")
        r2 = await client.get("/products?page=2&page_size=10")
    assert r1.status_code == 200
    assert r2.status_code == 200
    ids_page1 = {item["id"] for item in r1.json()["items"]}
    ids_page2 = {item["id"] for item in r2.json()["items"]}
    assert ids_page1.isdisjoint(ids_page2)
