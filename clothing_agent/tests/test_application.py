from app.main import app


def route_paths() -> set[str]:
    return {
        getattr(route, "path", "")
        for route in app.routes
        if getattr(route, "path", None)
    }


def test_current_agent_routes_exist():
    paths = route_paths()
    assert "/health" in paths
    assert "/health/ready" in paths
    assert "/api/v1/chat" in paths
    assert "/api/v1/conversations" not in paths
