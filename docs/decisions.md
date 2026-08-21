# Architectural Decision Records (ADR)

## ADR-001: Fitzy Agent Boundary Separation
- **Decision**: Keep the agent implementation in `clothing_agent/` separate from the commerce backend `clothing_app/`.
- **Rationale**: Ensures the agent consumes commerce capabilities strictly via the integration HTTP adapter boundary (`clothing_agent/app/integration/`).

## ADR-002: One Authoritative Promotion Evaluation Path
- **Decision**: Centralize promotion evaluation logic in `clothing_app/app/promotions/service.py` across catalog search, product detail display, cart preview, and order checkout.
- **Rationale**: Prevents price discrepancies between product cards, cart totals, and final order billing.

## ADR-003: Row Locking and Idempotent Checkout
- **Decision**: Use PostgreSQL `SELECT FOR UPDATE` row locking during order placement and validate stock availability post-lock. Accept an optional `checkout_request_id` for order idempotency.
- **Rationale**: Eliminates overselling under concurrent checkouts and prevents duplicate order creation.

## ADR-004: File-Backed Persistent Agent State Store
- **Decision**: Implement `FileConversationStateStore` in `clothing_agent/app/core/state_store.py` to persist `ConversationState` as JSON files.
- **Rationale**: Preserves session state across process restarts without adding Redis or external infrastructure to the V1 prototype.

## ADR-005: Store Tenancy Foundation
- **Decision**: Introduce `Store` entity and store-scoped unique constraints across branches, categories, products, variants, and offers.
- **Rationale**: Provides multi-tenant support for multi-brand deployment while maintaining single-store defaults.
