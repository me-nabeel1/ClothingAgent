# Module map

## Clothing application

| Module | Utility | Takes | Returns |
|---|---|---|---|
| `catalog/api.py` | Existing-app retrieval endpoints | Query parameters or `ProductSearchRequest` | Search results, product details, branches, availability |
| `catalog/service.py` | Search, ranking, details and stock validation | Validated catalog schemas | Stable catalog response schemas |
| `catalog/repository.py` | SQLAlchemy-only retrieval | Service filters | Flattened database rows kept private from APIs |
| `catalog/models.py` | Mapping of the existing `clothing_store` schema | SQLAlchemy sessions | ORM entities used only by repositories |
| `cart/api.py` | Minimum cart endpoints used by UI and agent | Cart IDs and cart request schemas | Complete `CartView` |
| `cart/service.py` | Validates price/stock before cart changes | Cart commands | Trusted cart state |
| `cart/repository.py` | Temporary process-local cart storage | Validated cart records | Mutable internal cart records |

The clothing application does not contain an LLM, router, conversation agent,
or admin product CRUD.

## Clothing agent

| Module | Utility | Takes | Returns |
|---|---|---|---|
| `orchestrator` | Executes one complete chat turn | `conversation_id`, customer message | Unified `ChatTurnResponse` |
| `router` | Detects domain, intent and specialist | Message plus conversation context | `RouteDecision` |
| `conversation` | Stores anonymous chat context locally | Messages, preferences, discovery stage, displayed history, selected product, cart ID | `ConversationState` / `ConversationView` |
| `llm/client.py` | One Groq chat-completions integration | LLM messages and optional Pydantic schema | Text or validated structured object |
| `clients/clothing_app` | Sole app-integration boundary | Typed product/cart requests | Typed clothing-app responses |
| `agents/sales` | Dynamic greeting, concise help and redirection | `AgentRequest` | `AgentResult` |
| `agents/shopping` | Guided discovery, selection, similar items, details and availability | Customer request and product context | Grounded reply plus product cards |
| `agents/fashion` | Domain-limited styling guidance | Customer request and preferences | Advice and optional matching products |
| `agents/cart` | Conversational cart behavior | Customer command, displayed products, cart | Grounded reply plus current cart |
| `tools/registry.py` | Named executable operations | Tool name and validated arguments | Tool result from clothing-app API |
| `core/container.py` | Wires clients, tools, agents and orchestrator | Root environment config | Process-wide dependency graph |


## Conversation-state fields

| Field | Purpose |
|---|---|
| `shopping_stage` | Controls whether the agent is new, clarifying, presenting, or handling a selection |
| `clarification_count` | Enforces the configured two-question ceiling |
| `preferences` | Keeps category, purpose, fit, size, color, budget, material, and branch context |
| `displayed_products` | Resolves current references such as “the second one” |
| `previous_displayed_products` | Preserves the prior result set when details or alternatives replace the cards |
| `selected_product` | Resolves pronouns such as “it” and supports stock/cart follow-ups |

## Boundary rules

1. Agents call tools, not the clothing application's database.
2. Tools call `ClothingAppClient`, not SQLAlchemy repositories.
3. The router selects an agent but never performs business actions.
4. Product facts must come from clothing-app API responses.
5. The LLM interprets language and composes responses; deterministic code
   validates IDs, prices, stock, cart quantities and routing fallbacks.
6. Every specialist returns the common `AgentResult`.

## Frontend

### `frontend/src/hooks/useChat.ts`

**Utility:** Owns the browser-side conversation lifecycle.

**Takes:** User text and UI action commands.

**Uses:** Clothing-agent conversation APIs and both health endpoints.

**Returns to components:** Timeline messages, current cart, loading/error state,
suggested actions, and service status.

### `frontend/src/api/agent.ts`

**Utility:** Typed HTTP boundary for the frontend.

**Takes:** Conversation IDs and message strings.

**Returns:** `ConversationStarted`, `ChatTurnResponse`, and health responses.

Product-image URLs are resolved against the clothing-app base URL. No database
or business logic is present in this layer.

### `frontend/src/components/MessageBubble.tsx`

**Utility:** Displays user/assistant messages and any product options returned
for that assistant turn.

**Takes:** One timeline message.

**Returns:** Message UI and action callbacks such as product details or add to
cart.

### `frontend/src/components/ProductCard.tsx`

**Utility:** Presents one exact branch-specific variant.

**Takes:** `ProductOption`, displayed position, and an action callback.

**Returns:** Natural-language commands such as `Add option 2 to my cart`. It
does not mutate the cart directly.

### `frontend/src/components/CartPanel.tsx`

**Utility:** Displays the latest cart returned by the cart agent.

**Takes:** `CartView` and action callback.

**Returns:** Conversational quantity, remove, clear, and browse commands. The
agent remains the single interaction path for cart operations in this demo.
