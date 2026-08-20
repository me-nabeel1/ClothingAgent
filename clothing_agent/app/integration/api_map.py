"""Current prototype commerce API map used by the Agent integration boundary.

This document-like module records the concrete endpoints already present in the
current commerce application.  Phase 1 does not implement HTTP calls; it fixes
semantic tool contracts first.  Phase 3 will implement the adapter against this
map without changing the commerce API unless a genuine incompatibility is found.
"""

from __future__ import annotations

CURRENT_API_MAP: dict[str, dict[str, object]] = {
    "get_products": {
        "method": "POST",
        "path": "/api/v1/products/search",
        "notes": "Primary structured catalog search contract. Existing backend also exposes GET /api/v1/products for UI-style filtering.",
    },
    "get_product_details": {
        "method": "GET",
        "path": "/api/v1/products/{product_id}",
        "notes": "Returns full product details and sellable branch options.",
    },
    "get_branches": {
        "method": "GET",
        "path": "/api/v1/branches",
        "notes": "Customer-facing branch discovery; branch is optional for normal shopping.",
    },
    "check_availability": {
        "method": "GET",
        "path": "/api/v1/inventory/availability",
        "notes": "Exact variant + branch availability. Branch is internal unless customer explicitly asks about a branch.",
    },
    "create_cart": {
        "method": "POST",
        "path": "/api/v1/cart",
        "notes": "Path should be confirmed against the concrete router before Phase 3 implementation; existing repository reports a create-cart operation.",
    },
    "get_cart": {
        "method": "GET",
        "path": "/api/v1/cart/{cart_id}",
        "notes": "Existing cart capability; exact route must be verified from current cart/api.py before wiring.",
    },
    "add_to_cart": {
        "method": "POST",
        "path": "/api/v1/cart/{cart_id}/items",
        "notes": "Existing cart capability; exact route must be verified from current cart/api.py before wiring.",
    },
    "update_cart": {
        "method": "PATCH",
        "path": "/api/v1/cart/{cart_id}/items/{item_id}",
        "notes": "Existing cart capability; exact route must be verified from current cart/api.py before wiring.",
    },
    "remove_from_cart": {
        "method": "DELETE",
        "path": "/api/v1/cart/{cart_id}/items/{item_id}",
        "notes": "Existing cart capability; exact route must be verified from current cart/api.py before wiring.",
    },
    "clear_cart": {
        "method": "DELETE",
        "path": "/api/v1/cart/{cart_id}/items",
        "notes": "Existing cart capability; exact route must be verified from current cart/api.py before wiring.",
    },
}
