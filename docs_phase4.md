# Phase 4 — Fitzy Runtime

Phase 4 connects the LLM to the existing Phase 2 planner/execution engine and
Phase 3 commerce adapter.

Runtime flow:

```text
Customer message
    ↓
IntentExtraction (LLM)
    ↓
ConversationState
    ↓
ActionPlanner
    ↓
ToolRequirementChecker
    ↓
parallel/dependency-aware execution
    ↓
CommerceToolAdapter
    ↓
existing Northstar REST API
    ↓
authoritative result
    ↓
state update
    ↓
language-safe response generation
```

The LLM never calculates commerce truth. The backend remains authoritative.

The runtime supports English, Urdu script, and Roman Urdu. Devanagari output is
rejected and regenerated once; a second unsafe result raises an error rather
than leaking Hindi output to customers.

## Environment

Configure an OpenAI-compatible endpoint with:

- `FITZY_LLM_BASE_URL`
- `FITZY_LLM_API_KEY`
- `FITZY_LLM_MODEL`

The provider adapter uses the standard `/chat/completions` endpoint.

## HTTP surface

The Agent route is defined at:

`POST /api/v1/agent/chat`

Request:

```json
{
  "session_id": "demo-session-1",
  "message": "mujhe black shirts dikhao"
}
```

Response:

```json
{
  "session_id": "demo-session-1",
  "response": "Bilkul, yeh available black shirts hain..."
}
```

The application bootstrap must inject the configured `FitzyAgent` instance into
`get_agent`.
