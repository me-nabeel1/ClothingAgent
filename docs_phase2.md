# Phase 2 Design Notes

## Flow

User message → structured intent extraction → dependency-aware action plan → requirement check → execute ready actions → wait for missing customer input → resume the plan.

## Parallelism

Independent read operations are siblings in the action graph and can execute concurrently. Data-dependent operations wait for their dependency. Confirmation-dependent mutations remain blocked until the required state is explicitly established.

## Automatic prerequisites

If a requested mutation needs a cart and no cart is known, the planner may insert `CREATE_CART`. If `PLACE_ORDER` is requested without an existing checkout result/action, the planner inserts `PREVIEW_CHECKOUT` before `PLACE_ORDER`.

## Real API boundary

The planner uses semantic `ToolName` values only. Concrete endpoint paths, request translation, and response mapping remain in Phase 3 integration adapters so the existing prototype APIs can be reused without frontend changes.
