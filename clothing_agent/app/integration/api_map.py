"""Concrete endpoint map for the existing Northstar prototype APIs.

Phase 3 treats these routes as an external application contract. The Agent
semantic contracts remain stable even if a future brand exposes different
paths. Only this integration map/client should need adaptation.
"""

from __future__ import annotations

CURRENT_API_MAP: dict[str, dict[str, object]] = {
    "get_products": {"method": "POST", "path": "/api/v1/products/search"},
    "get_product_details": {"method": "GET", "path": "/api/v1/products/{product_id}"},
    "get_branches": {"method": "GET", "path": "/api/v1/branches"},
    "check_availability": {"method": "GET", "path": "/api/v1/inventory/availability"},
    "create_cart": {"method": "POST", "path": "/api/v1/carts"},
    "get_cart": {"method": "GET", "path": "/api/v1/carts/{cart_id}"},
    "add_to_cart": {"method": "POST", "path": "/api/v1/carts/{cart_id}/items"},
    "update_cart": {"method": "PATCH", "path": "/api/v1/carts/{cart_id}/items/{item_id}"},
    "remove_from_cart": {"method": "DELETE", "path": "/api/v1/carts/{cart_id}/items/{item_id}"},
    "clear_cart": {"method": "DELETE", "path": "/api/v1/carts/{cart_id}/items"},
    "preview_checkout": {"method": "POST", "path": "/api/v1/carts/{cart_id}/preview"},
    "place_order": {"method": "POST", "path": "/api/v1/orders"},
    "get_store_context": {
        "method": None,
        "path": None,
        "status": "not_exposed_by_current_main_branch_api",
        "notes": "Do not invent an endpoint. Derive future store context from existing catalog/branch APIs or add a real backend endpoint only after proving it is necessary."
    },
}
