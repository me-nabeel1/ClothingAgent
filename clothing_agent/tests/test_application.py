from app.main import app


def route_paths() -> set[str]:
    paths: set[str] = set()
    for route in app.routes:
        path = getattr(route, "path", None)
        if path:
            paths.add(path)
            continue

        original_router = getattr(route, "original_router", None)
        include_context = getattr(route, "include_context", None)
        if original_router is None or include_context is None:
            continue
        prefix = include_context.prefix.rstrip("/")
        paths.update(f"{prefix}{item.path}" for item in original_router.routes)
    return paths


def test_expected_agent_routes_exist():
    paths = route_paths()
    assert "/health" in paths
    assert "/health/ready" in paths
    assert "/api/v1/conversations" in paths
    assert "/api/v1/conversations/{conversation_id}/messages" in paths
