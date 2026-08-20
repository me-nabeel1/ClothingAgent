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
|  | /api/v1/orders   |  | /api/v1/promotions|  | /api/v1/chat       |  |
|  +------------------+  +-------------------+  +--------------------+  |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
|                    PostgreSQL Database (clothing_store)              |
+-----------------------------------------------------------------------+
```

## Bounded Contexts

The application core (`app/`) is organized into clean domain-driven bounded contexts:

- **Catalog (`app/catalog/`)**: Manages products, categories, variants, colors, sizes, and product images.
- **Inventory (`app/inventory/`)**: Tracks branch-level stock availability and inventory reservations.
- **Cart (`app/cart/`)**: Handles session-bound shopping cart creation, item additions, quantity updates, and cart preview/totals.
- **Orders (`app/orders/`)**: Handles order placement, validation, status tracking, and order persistence.
- **Promotions (`app/promotions/`)**: Evaluates promotional discounts, offers, and storewide deals.
- **Common (`app/common/`)**: Shared enums, exceptions, logging observability, and attribute normalizers (`helpers.py`).

## Architectural Boundaries

1. **Isolation**: Commerce domain services interact through clear interfaces and database repositories without cross-domain leakages.
2. **Agent Separation**: The Fitzy agent implementation resides in a standalone package (`clothing_agent/`), consuming commerce capabilities strictly via the integration HTTP adapter (`clothing_agent/app/integration/`).
3. **Database Ownership**: All persistence logic is encapsulated within SQLAlchemy repository classes using async sessions (`app/database.py`).
