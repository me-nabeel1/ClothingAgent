# Clothing Sales Demo Frontend

React/Vite presentation layer for the clothing-app and clothing-agent services.
It uses the agent API for every conversational action. Product images are read
from the clothing app's local static-assets endpoint.

## Shared configuration

Vite loads environment variables from the workspace-level `.env` through
`envDir: ".."` in `vite.config.ts`.

Required values:

```env
VITE_AGENT_API_URL=http://127.0.0.1:8000
VITE_CLOTHING_APP_URL=http://127.0.0.1:8100
VITE_APP_NAME=Atelier AI
```

## Run

From the workspace root:

```powershell
npm install --prefix frontend
npm run frontend:dev
```

Open `http://localhost:5173`.

## Interaction design

- Product-card buttons send natural commands such as `Add option 2 to my cart`.
- Cart quantity and removal controls also send commands through the agent.
- The frontend does not directly alter catalog, stock, or cart storage.
- Service-status indicators use the health endpoints exposed by both backends.
