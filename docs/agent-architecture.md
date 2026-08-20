# Fitzy Single-Agent Architecture

## Overview

Fitzy is a single-agent salesperson architecture designed for precision customer assistance, catalog navigation, requirement checking, action planning, and semantic-to-HTTP adaptation.

```
+-------------------------------------------------------------------+
|                        Fitzy Agent Core                           |
|  (clothing_agent/app/agent/)                                      |
|                                                                   |
|  +--------------------+  +---------------------+                  |
|  | Tool Contracts     |  | Requirement Checker |                  |
|  | (contracts.py)     |  | (requirements.py)   |                  |
|  +--------------------+  +---------------------+                  |
|  | Conversation State |  | Action Planner      |                  |
|  | (state.py)         |  | (planner.py)        |                  |
|  +--------------------+  +---------------------+                  |
|  | Execution Engine   |  | Intent Extractor    |                  |
|  | (execution.py)     |  | (intent.py)         |                  |
|  +--------------------+  +---------------------+                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       Integration Boundary                        |
|  (clothing_agent/app/integration/)                                |
|                                                                   |
|  +--------------------+  +---------------------+                  |
|  | CommerceAPIClient  |  | CommerceToolAdapter |                  |
|  | (client.py)        |  | (client.py)         |                  |
|  +--------------------+  +---------------------+                  |
|  | API Mapping        |  | Async Transport     |                  |
|  | (api_map.py)       |  | (http.py)           |                  |
|  +--------------------+  +---------------------+                  |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                   Existing Commerce REST APIs                     |
|                   (/api/v1/products/search, /api/v1/carts, etc.)    |
+-------------------------------------------------------------------+
```

## Agent Components

1. **Contracts (`contracts.py`)**: Declares strict tool definitions (`GET_PRODUCTS`, `GET_PRODUCT_DETAILS`, `ADD_TO_CART`, `PREVIEW_CHECKOUT`, `PLACE_ORDER`, etc.), tool parameter requirements, and parameter types.
2. **Requirements Checker (`requirements.py`)**: Validates missing mandatory parameters and checks if state values satisfy execution prerequisites.
3. **Conversation State (`state.py`)**: Maintains customer preferences, active search state, cart state, action plan, and turn history across chat turns.
4. **Action Planner (`planner.py`)**: Generates structured action plans with dependency graphs (e.g., product search completed before cart addition).
5. **Execution Engine (`execution.py`)**: Coordinates tool execution, updates action statuses (`PENDING`, `READY`, `COMPLETED`, `FAILED`), and updates conversation state upon completion.
6. **Integration Boundary (`integration/`)**: Translates high-level semantic tool calls into HTTP requests against existing Northstar APIs without exposing backend paths or HTTP details to the agent.
