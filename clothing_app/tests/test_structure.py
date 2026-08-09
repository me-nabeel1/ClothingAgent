"""Small structural tests that do not require a running PostgreSQL server."""

from app.main import app
from fastapi.routing import APIRoute


def api_route_records() -> set[tuple[str, str]]:
    """Return API method/path pairs across direct and included routers."""

    records: set[tuple[str, str]] = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            records.update((method, route.path) for method in route.methods)
            continue

        original_router = getattr(route, "original_router", None)
        include_context = getattr(route, "include_context", None)
        if original_router is None or include_context is None:
            continue

        prefix = include_context.prefix.rstrip("/")
        for included_route in original_router.routes:
            if isinstance(included_route, APIRoute):
                records.update(
                    (method, f"{prefix}{included_route.path}")
                    for method in included_route.methods
                )
    return records


def test_only_required_api_routes_are_exposed() -> None:
    """Prevent accidental reintroduction of admin CRUD or AI endpoints."""

    routes = api_route_records()
    expected = {
        ("GET", "/health"),
        ("GET", "/health/ready"),
        ("GET", "/api/v1/products"),
        ("POST", "/api/v1/products/search"),
        ("GET", "/api/v1/products/{product_id}"),
        ("GET", "/api/v1/branches"),
        ("GET", "/api/v1/inventory/availability"),
        ("POST", "/api/v1/carts"),
        ("GET", "/api/v1/carts/{cart_id}"),
        ("POST", "/api/v1/carts/{cart_id}/items"),
        ("PATCH", "/api/v1/carts/{cart_id}/items/{item_id}"),
        ("DELETE", "/api/v1/carts/{cart_id}/items/{item_id}"),
        ("DELETE", "/api/v1/carts/{cart_id}/items"),
    }
    assert expected.issubset(routes)

    forbidden_fragments = ("/orders", "/agents", "/conversations", "/admin")
    assert not any(
        fragment in path
        for _, path in routes
        for fragment in forbidden_fragments
    )


def test_temporary_cart_can_be_created_and_read() -> None:
    """Verify the demo cart lifecycle without requiring PostgreSQL."""

    from app.database import get_db
    from fastapi.testclient import TestClient

    async def fake_db():
        # Cart creation/read does not access the catalog database.
        yield object()

    app.dependency_overrides[get_db] = fake_db
    with TestClient(app) as client:
        created = client.post("/api/v1/carts")
        assert created.status_code == 201
        body = created.json()
        assert body["items"] == []
        assert body["subtotal"] in ("0.00", "0.0", "0")

        fetched = client.get(f"/api/v1/carts/{body['cart_id']}")
        assert fetched.status_code == 200
        assert fetched.json()["cart_id"] == body["cart_id"]

    app.dependency_overrides.clear()
