# Northstar Commerce REST API Reference

All backend API routes are exposed under the `/api/v1` prefix.

## 1. Catalog & Discovery

### `POST /api/v1/products/search`
Search catalog products with structured filters.
- **Request Body**:
  ```json
  {
    "query_text": "shirt",
    "category": "Shirts",
    "colors": ["Black"],
    "size_mapping": {"L": "L"},
    "minimum_price": 1000,
    "maximum_price": 6000,
    "limit": 10
  }
  ```
- **Response**: `200 OK` — `ProductSearchResponse` (`products: List[ProductCard]`, `result_count: int`)

### `GET /api/v1/products`
UI-oriented product listing endpoint translating query parameters into structured catalog search.

### `GET /api/v1/products/{product_id}`
Retrieve detailed product specifications, variants, and branch stock.

### `GET /api/v1/branches`
List store branches (`branch_id`, `branch_code`, `branch_name`, `city`, `address`).

---

## 2. Inventory

### `GET /api/v1/inventory/availability`
Check stock availability for a specific variant and branch.

---

## 3. Cart Management

### `POST /api/v1/carts`
Initialize a new shopping cart. Accepts optional `session_id` and `store_id`.

### `GET /api/v1/carts/{cart_id}`
Retrieve cart state and item details.

### `POST /api/v1/carts/{cart_id}/items`
Add an item variant to cart.

### `POST /api/v1/carts/{cart_id}/preview`
Preview cart totals, applicable discounts, free delivery eligibility, and grand total.

---

## 4. Orders

### `POST /api/v1/orders`
Place a customer order with idempotency protection and atomic inventory deduction.
- **Request Body**:
  ```json
  {
    "cart_id": "uuid-string",
    "checkout_request_id": "optional-idempotency-key",
    "customer_name": "Ahmed Khan",
    "phone": "03001234567",
    "delivery_address": "House 1, Street 2, F-7",
    "city": "Islamabad",
    "explicit_confirmation": true
  }
  ```

---

## 5. Fitzy Agent Chat

### `POST /api/v1/agent/chat`
Process a customer message through the single-agent concierge.
- **Request Body**: `{"session_id": "demo-1", "message": "Show me black shirts"}`
- **Response**: `{"session_id": "demo-1", "response": "Here are the available black shirts..."}`
