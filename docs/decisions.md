# Architectural Decision Records (ADR)

## ADR-001: Fitzy Agent Boundary Separation
- **Decision**: Keep the agent implementation in `clothing_agent/` completely separate from the commerce backend `app/`.
- **Rationale**: Ensures the agent relies strictly on semantic tool contracts and the integration HTTP adapter boundary, preventing tight coupling to database schemas or SQLAlchemy models.

## ADR-002: Preservation of Existing Commerce API Endpoints
- **Decision**: Maintain all existing `/api/v1/*` endpoints without redesigning or inventing agent-specific endpoints.
- **Rationale**: Protects frontend contract stability and avoids backend fragmentation.

## ADR-003: Integration Layer Request Translation & Fan-Out
- **Decision**: Handle multi-category query fan-out and transport-level size flattening inside `CommerceAPIClient` in the integration layer (`clothing_agent/app/integration/client.py`).
- **Rationale**: Preserves rich semantic agent state model (`size_mapping`, multiple categories) while adhering to backend REST endpoint schema restrictions.

## ADR-004: Centralization of Attribute Normalizers
- **Decision**: Consolidate multilingual size, color, and category normalizers into `app/common/helpers.py`.
- **Rationale**: Removes duplicated helper logic across domain modules and legacy agent directories.
