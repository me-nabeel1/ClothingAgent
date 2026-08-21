# V1 Backend + Agent Hardening Patch

## Scope

This patch hardens the existing Northstar prototype without redesigning its public API surface. It keeps Fitzy as a consumer of the commerce API and centralizes backend business truth in the commerce domains.

## P0 fixes

- Fixed stale `ProductSearchRequest.sizes` references to use `size_mapping`.
- Preserved the legacy `GET /api/v1/products` route while translating its legacy query parameters into the structured search contract.
- Added category-aware promotion evaluation.
- Added authoritative free-delivery promotion handling during checkout.
- Consolidated catalog product-level promotion evaluation onto the same promotion rule helper used by checkout.
- Made the request-scoped database dependency commit successful mutations and roll back failed requests.
- Added order-time row locking and post-lock stock validation.
- Added checkout-request idempotency to prevent duplicate order creation.
- Added TTL inventory reservations so cart quantities are temporarily held and converted into stock deductions only when an order is placed.

## P1 fixes

- Added `Store` tenancy and store-scoped unique keys for branches, categories, products, variants, and offers.
- Added cart/order store foreign keys and store filtering.
- Centralized product image URL resolution in `app/common/media.py`.
- Removed duplicate health-route registration; `/health` and `/health/ready` remain unprefixed, matching Docker readiness checks.
- Standardized inventory access through `InventoryRepository` instead of incorrectly reusing `CatalogRepository`.
- Added database-level cart/inventory/promotion invariants.
- Added validation for impossible search price ranges.
- Replaced multiple active seed/bootstrap paths with Alembic + `clothing_app/scripts/seed.py` as the canonical initialization path.
- Removed tracked runtime logs and obsolete manual SQL/test seed artifacts from the active project tree.
- Moved the destructive database reset helper to `tools/reset_demo_db.py`.

## P2 foundations

- Added file-backed persistent Agent session state through `ConversationStateStore`; the storage boundary is replaceable by a database/Redis implementation later.
- Added a volume for Agent state in Docker Compose.
- Added explicit authentication and payment provider protocols without coupling V1 to a vendor.
- Added store tenancy primitives and store-scoped uniqueness as a foundation for multiple client brands.
- Added reservation primitives that can later be moved to a dedicated expiry worker.
- Kept authentication/payment execution disabled until a real provider contract is supplied.

## API compatibility

The existing commerce routes remain the same. The cart create endpoint additionally accepts an optional JSON body containing `session_id` and `store_id`, while an empty request remains valid for existing clients.

The order request accepts an optional `checkout_request_id`; when omitted, the backend generates one, preserving existing clients.

## Verification

- `python -m compileall clothing_app clothing_agent` — passed.
- `PYTHONPATH=clothing_app pytest clothing_app/tests -q` — **7 passed, 1 skipped**.
- `PYTHONPATH=clothing_agent pytest clothing_agent/tests -q` — **38 passed**.
- `alembic upgrade head --sql` — migration chain generated successfully through `e4c2a1b7d9f4`.
- Docker Compose YAML parsed successfully with PyYAML.

## Known V1 boundary

The hardening patch does not implement a real authentication server or real payment gateway because those require an external provider contract. Provider interfaces are present so the order domain does not need to be redesigned when those integrations are introduced.
