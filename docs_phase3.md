# Fitzy Phase 3 — Existing API Adapter + Tool Boundary

## Objective

Map the Phase 1/2 semantic Agent contracts onto the current Northstar prototype APIs without changing those APIs.

## Confirmed API surface

- `POST /api/v1/products/search`
- `GET /api/v1/products/{product_id}`
- `GET /api/v1/branches`
- `GET /api/v1/inventory/availability`
- `POST /api/v1/carts`
- `GET /api/v1/carts/{cart_id}`
- `POST /api/v1/carts/{cart_id}/items`
- `PATCH /api/v1/carts/{cart_id}/items/{item_id}`
- `DELETE /api/v1/carts/{cart_id}/items/{item_id}`
- `DELETE /api/v1/carts/{cart_id}/items`
- `POST /api/v1/carts/{cart_id}/preview`
- `POST /api/v1/orders`

## Critical integration rule

The Agent's semantic contracts are stable. The `CommerceAPIClient` is the adaptation boundary. Do not put route names, HTTP verbs, backend field quirks, or response-shape compatibility logic into `SingleAgent`, the planner, or the requirement checker.

### Existing endpoint adaptation

The current product search API accepts a single `category` and flat `sizes`, while the Agent contract accepts multiple categories and semantic `size_mapping`. The adapter therefore:

1. fans out multiple category searches when necessary;
2. flattens size values only at the transport boundary;
3. preserves semantic size mapping in Agent state/contracts;
4. merges results deterministically;
5. never changes the backend API.

## Store context

The current catalog API mapping does not expose a dedicated `/store/context` endpoint in the confirmed main-branch catalog routes. Phase 3 intentionally does not invent one. A future context layer may derive context from existing catalog/branch APIs or add a real backend capability only when a concrete requirement proves it necessary.

## Phase 3 boundaries

Phase 3 implements:

- asynchronous HTTP transport;
- semantic commerce client;
- typed/normalized transport schemas;
- semantic tool dispatcher;
- error translation;
- API mapping tests.

Phase 3 does NOT implement:

- LLM intent extraction;
- SingleAgent orchestration;
- final tool requirement workflow;
- frontend changes;
- backend endpoint changes;
- authentication/payment/Shopify/Stripe;
- a new commerce API.
