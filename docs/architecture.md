# Northstar Commerce Application Architecture

## System Overview

The Northstar Commerce Application is a single-port FastAPI microservice that unifies e-commerce domain APIs (`catalog`, `cart`, `inventory`, `orders`, `promotions`) with an AI Sales Concierge agent (`Fitzy`).

```
+-----------------------------------------------------------------------+
|                             Frontend (Vite/React)                     |
+-----------------------------------------------------------------------+
                                   |
                                   | HTTP REST
                                   v
+-----------------------------------------------------------------------+
|                    FastAPI Unified Service (/api/v1)                  |
|                                                                       |
|  +------------------+  +-------------------+  +--------------------+  |
|  | Catalog Domain   |  | Inventory Domain  |  | Cart Domain        |  |
|  | /api/v1/products |  | /api/v1/inventory |  | /api/v1/carts      |  |
|  +------------------+  +-------------------+  +--------------------+  |
|  | Orders Domain    |  | Promotions Domain |  | Fitzy Agent        |  |
|  | /api/v1/orders   |  | /api/v1/promotions|  | /api/v1/agent/chat |  |
|  +------------------+  +-------------------+  +--------------------+  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    PostgreSQL Database (clothing_store)              |
+-----------------------------------------------------------------------+
```

## Hardened Backend Bounded Contexts (`clothing_app/app/`)

- **Store Tenancy**: Multi-store tenant foundation with store-scoped unique constraints (`stores`, `store_id`).
- **Catalog (`app/catalog/`)**: Manages products, categories, variants, colors, sizes, and product images using `size_mapping` and centralized media resolution (`app/common/media.py`).
- **Inventory (`app/inventory/`)**: Managed via `InventoryRepository` with row locking (`SELECT FOR UPDATE`), stock revalidation during checkout, and TTL reservation holds.
- **Cart (`app/cart/`)**: Cart creation with optional `session_id` and `store_id`, item quantity updates, session isolation, and reservation conversion.
- **Orders (`app/orders/`)**: Order placement with idempotency (`checkout_request_id`), transaction boundaries (automatic rollback on error), stock revalidation, and auth/payment provider boundaries.
- **Promotions (`app/promotions/`)**: Authoritative promotion rule evaluation supporting global store, branch, category, product, and free-delivery discounts across listing, cart, and checkout.
- **Common (`app/common/`)**: Centralized media URL creation, custom exception handlers, and observability.

## Agent Package (`clothing_agent/app/`)

- **Fitzy Agent Core**: Conversational intent extraction, requirements validation, action planning, tool execution, and response generation with language safety.
- **Persistent State Store (`FileConversationStateStore`)**: Atomic file-backed persistence for `ConversationState` surviving process restarts.
- **Integration Boundary (`app/integration/`)**: Translates high-level semantic tools into HTTP requests against `/api/v1/*` REST APIs.
