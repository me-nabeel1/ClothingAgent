# Backend Hardening Report

## Overview
This document summarizes the architectural and code-level hardening rules implemented for the V1 Clothing Commerce Backend (`clothing_app`) and AI Sales Agent (`clothing_agent`).

## Hardening Invariants

### 1. Multi-Tenancy & Isolation
- All database entities operate under an explicit `store_id` (default: `northstar`).
- Tenancy constraints are enforced via composite unique keys (`store_id`, `article_code`), (`store_id`, `sku`), etc.

### 2. Inventory Reservations
- Inventory holds are managed deterministically via `ReservationService`.
- `ReservationService.reserve()` internally calculates total inventory availability and enforces the invariant:
  $$\text{new\_reserved\_total} \le \text{available\_quantity}$$
- Caller routines (such as `CartService`) do not need to release existing holds prior to calling `reserve()`.

### 3. Checkout Confirmation Invalidation
- A checkout preview (`POST /api/v1/carts/{id}/preview`) generates an authoritative confirmation context.
- Any subsequent cart mutation (`add`, `remove`, `update`, `clear`) immediately invalidates the pending confirmation context.
- `OrderService.place_order` verifies that a valid confirmation exists for the current cart state before committing the order.
- The AI Agent runtime (`clothing_agent`) invalidates its internal confirmation state whenever cart mutation intents occur, preventing stale orders.

### 4. Order Idempotency
- `OrderService.place_order` relies on `checkout_request_id`.
- Duplicate submissions with the same `checkout_request_id` return the previously generated order snapshot without duplicate processing or inventory re-deduction.

### 5. Repository Cleanliness
- Application code is completely partitioned into `clothing_app/` and `clothing_agent/`.
- Temporary logs and runtime caches are strictly gitignored.
- Seeding and database reset utilities are unified under `clothing_app/scripts/seed.py` and `tools/reset_demo_db.py`.
