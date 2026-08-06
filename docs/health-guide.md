# Health and diagnostics guide

## Clothing application

- `GET http://127.0.0.1:8100/health` confirms FastAPI is running.
- `GET http://127.0.0.1:8100/health/ready` verifies PostgreSQL connectivity.

When readiness fails, check `CLOTHING_APP_DATABASE_URL`, PostgreSQL service
status, database name, password encoding, and whether the existing
`clothing_store` schema is present.

## Clothing agent

- `GET http://127.0.0.1:8000/health` lists registered agents and tools and shows
  whether an LLM key is configured.
- `GET http://127.0.0.1:8000/health/ready` verifies the clothing-app dependency.

Expected dependencies:

```json
{
  "status": "ready",
  "clothing_app": {
    "status": "ready",
    "database": "connected"
  },
  "llm": "configured"
}
```

When no LLM key is configured and local fallback is enabled, `llm` reports
`local_fallback`. This is acceptable for basic wiring tests, but full natural
routing and response quality require a working API key.

## Common errors

### Agent cannot reach clothing app

Confirm the clothing app is running on port 8100 and that `.env` contains:

```env
CLOTHING_AGENT_CLOTHING_APP_BASE_URL=http://127.0.0.1:8100
```

### LLM unavailable

Check the key, model slug, internet connection and free-model rate limits. Keep
`CLOTHING_AGENT_ALLOW_LOCAL_FALLBACK=true` during local development.

### `No module named app`

Run both commands from the workspace root and include the correct app directory:

```powershell
uvicorn app.main:app --app-dir clothing_app --port 8100
uvicorn app.main:app --app-dir clothing_agent --port 8000
```

### Product database column mismatch

The included clothing-app mappings intentionally omit the legacy `products.tags`
and `products.attributes` columns because the current local database does not
contain them. Product search uses existing fields such as name, description,
material, fit, season and category.

## Frontend

Run the Vite frontend from the workspace root:

```powershell
npm install --prefix frontend
npm run frontend:dev
```

Open `http://localhost:5173`. Use `localhost`, not `127.0.0.1`, because both
backend CORS configurations allow the shared origin `http://localhost:5173`.

The header shows:

- `Agent`: the clothing-agent health status.
- `Catalog`: the clothing-app/database readiness status.

If the page opens but cannot start a conversation, verify ports 8000 and 8100
and check the browser Network tab for CORS or connection errors.
## Rotating logs and flow audit

The services create these files automatically under the root `logs/` directory:

- `clothing_agent.log` — agent requests, clothing-app dependency calls, and errors
- `clothing_app.log` — catalog/cart requests, database failures, and schema errors
- `sales_flow_audit.log` — conversation stages, route decisions, clarification
  counts, inventory searches, displayed-product counts, cart counts, and latency

Each request receives an `X-Request-ID` response header. Error responses contain
the same ID. Search that value across the logs to trace one request end to end.

Follow logs live in PowerShell:

```powershell
Get-Content .\logs\clothing_agent.log -Wait
Get-Content .\logs\clothing_app.log -Wait
Get-Content .\logs\sales_flow_audit.log -Wait
```

Filter one request or conversation:

```powershell
Select-String -Path .\logs\*.log -Pattern "REQUEST_OR_CONVERSATION_ID"
```

The files rotate at approximately 5 MB and retain five backups by default.
Adjust the `*_LOG_MAX_BYTES` and `*_LOG_BACKUP_COUNT` values in `.env`. API keys
and complete LLM prompts are intentionally excluded from logs.

