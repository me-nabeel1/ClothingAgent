# Clothing Sales Demo

This workspace contains the two backend concerns needed for the demo while
using **one virtual environment, one dependency file, and one root environment
file**.

```text
clothing_sales_demo/
├── clothing_app/       Existing-app simulation: catalog, inventory, cart APIs
├── clothing_agent/     AI salesperson: router, specialist agents, API tools
├── frontend/           React chat, product cards, service status, cart drawer
├── local/              Locally served product images
├── docs/
├── requirements.txt    Shared Python dependencies
├── package.json        Root frontend convenience scripts
└── .env.example        Shared configuration for all three surfaces
```

The services remain separate processes because the agent must demonstrate that
it retrieves data through application APIs rather than importing database
repositories. They still use the same `.venv` and `.env`.

## Runtime flow

```text
React frontend :5173
    -> Clothing agent API :8000
    -> Intent router
    -> Sales / Shopping / Fashion / Cart agent
    -> Registered tool
    -> Clothing app API :8100
    -> SQLAlchemy
    -> Local ClothingAppDummyDB
```

The clothing agent has no PostgreSQL driver usage, ORM models, or direct database
queries.

## 1. Create the unified environment

Run these commands from the workspace root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set the real PostgreSQL password:

```env
CLOTHING_APP_DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@127.0.0.1:5432/ClothingAppDummyDB
```

Add your Groq key to enable full LLM routing and response generation:

```env
CLOTHING_AGENT_LLM_API_BASE=https://api.groq.com/openai/v1
CLOTHING_AGENT_LLM_API_KEY=gsk_your_key
CLOTHING_AGENT_LLM_MODEL=llama-3.3-70b-versatile
```

The LLM client uses Groq's OpenAI-compatible `/chat/completions` endpoint.
Structured routing and extraction use JSON-object mode followed by Pydantic
validation, keeping the integration small and compatible with optional fields.

## 2. Start the clothing application

Open terminal 1 at the workspace root and activate the same `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir clothing_app --reload --reload-dir clothing_app --port 8100
```

Verify:

```text
http://127.0.0.1:8100/health
http://127.0.0.1:8100/health/ready
http://127.0.0.1:8100/docs
```

## 3. Start the clothing agent

Open terminal 2 at the workspace root and activate the same `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --app-dir clothing_agent --reload --reload-dir clothing_agent --port 8000
```

Verify:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/health/ready
http://127.0.0.1:8000/docs
```

`/health/ready` confirms the agent can reach the clothing application. It reports
whether the LLM is configured or whether the local fallback is active.


## 4. Start the frontend

Open terminal 3 at the workspace root:

```powershell
npm install --prefix frontend
npm run frontend:dev
```

Open:

```text
http://localhost:5173
```

The frontend reads its URLs from the same root `.env` file. Product-card and
cart controls send natural-language commands through the agent, so the demo
exercises routing, specialist agents, tools, application APIs, and live local
inventory end to end.

## Guided sales flow

The agent does not send an assistant message when a conversation is created. It
waits for the customer and then moves through a small conversation state:

```text
new -> clarifying -> presented -> selected -> cart
```

Broad requests trigger at most two focused questions. Fully specified requests
search immediately. Preferences and product references remain attached to the
conversation.

Example:

```text
Customer: I want to buy shirts.
Agent: What kind of shirt do you need—casual, office/formal, gym, or for an occasion?
Customer: Casual for summer.
Agent: Do you prefer a relaxed fit, regular fit, or something more fitted?
Customer: Relaxed.
Agent: I found three good options. I’d start with ...
Customer: The second one looks good.
Agent: Good pick—... Want me to check stock or add it to your cart?
```

## Agent APIs

Start a conversation:

```http
POST /api/v1/conversations
```

Send a message:

```http
POST /api/v1/conversations/{conversation_id}/messages
Content-Type: application/json

{
  "message": "Show me comfortable black trousers in size 34 under PKR 5000."
}
```

Get the conversation:

```http
GET /api/v1/conversations/{conversation_id}
```

## Supported behavior

- No assistant message before the customer speaks
- Short, dynamic salesperson greetings and general shopping assistance
- Domain restriction for unrelated requests
- Guided product discovery with at most two focused clarification questions
- Product search with saved category, purpose, fit, color, size, price, material and branch context
- Product detail and availability follow-ups
- Fashion advice with optional inventory search
- Conversational cart create, view, add, update, remove and clear
- References such as “the second one,” “previous one,” and “show similar” through display history
- Deterministic fallback when the LLM is temporarily unavailable

## Tests

Run each service's tests separately because both services intentionally use the
standard package name `app` inside separate process roots:

```powershell
$env:PYTHONPATH = "$PWD\clothing_app"
pytest clothing_app/tests -q

$env:PYTHONPATH = "$PWD\clothing_agent"
pytest clothing_agent/tests -q
```

See [docs/module-map.md](docs/module-map.md) for module inputs, outputs, and
ownership, and [docs/health-guide.md](docs/health-guide.md) for diagnostics.
