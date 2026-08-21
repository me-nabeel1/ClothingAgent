# Phase 4.1 — Runtime Hardening

This pass hardens the Phase 4 runtime without changing the Northstar commerce API.

## Fixes

1. Effective product search combines persistent preferences, active search state and current-turn overrides.
2. Delivery information accumulates safely across turns.
3. Waiting actions reopen when the next customer turn may satisfy their missing requirements.
4. Ordinary online shopping can deterministically resolve an internal fulfillment branch rather than forcing the customer to choose a branch.
5. Response-generation context is scoped to the current execution cycle rather than the entire historical tool-result dictionary.
6. Conversation state now exposes a simple delivery-completeness check.

## Intentional V1 limitation

Conversation state remains process-local. A future production deployment should externalize conversational state when multiple workers or restarts must preserve sessions.
