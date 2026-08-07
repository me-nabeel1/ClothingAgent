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

## 1. Configure the Environment

Copy the Docker environment template:

```powershell
Copy-Item .env.example .env
```

Add your Groq key in `.env` to enable full LLM routing and response generation:

```env
GROQ_API_KEY=gsk_your_key
CLOTHING_AGENT_LLM_API_BASE=https://api.groq.com/openai/v1
CLOTHING_AGENT_LLM_MODEL=llama-3.3-70b-versatile
```

The LLM client uses Groq's OpenAI-compatible `/chat/completions` endpoint.

## 2. Start the Docker Stack

The Inventory App, AI Agent, and Frontend are fully Dockerized and orchestrated via `docker-compose`.

Run this command from the workspace root:

```powershell
docker-compose up -d --build
```

Verify the services are running:

```powershell
docker-compose ps
```

The services will be available at:
- **Frontend**: http://localhost:8080
- **Agent API**: http://localhost:8000/docs
- **Clothing App API**: http://localhost:8100/docs

To stop the stack, run:
```powershell
docker-compose down
```

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

The agent API has been consolidated into a single endpoint for the MVP:

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "Show me comfortable black trousers in size 34 under PKR 5000.",
  "conversation_id": "optional-uuid-here"
}
```

If `conversation_id` is omitted, a new conversation is automatically created.

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
