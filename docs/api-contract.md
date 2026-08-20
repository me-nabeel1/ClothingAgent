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
    "sizes": ["L"],
    "minimum_price": 1000,
    "maximum_price": 6000,
    "limit": 10
  }
  ```
- **Response**: `200 OK` — `ProductSearchResponse` (`products: List[ProductCard]`, `result_count: int`)

### `GET /api/v1/products`
UI-oriented product listing endpoint with query parameters.

### `GET /api/v1/products/{product_id}`
Retrieve detailed product specifications, variants, and branch stock.

### `GET /api/v1/branches`
List all store branches (`branch_id`, `branch_code`, `branch_name`, `city`, `address`).

---

## 2. Inventory

### `GET /api/v1/inventory/availability`
Check stock availability for a specific variant and branch.

- **Query Parameters**: `variant_id` (int), `branch_id` (int)
- **Response**: `200 OK` — `AvailabilityView` (`variant_id`, `branch_id`, `available_quantity`, `is_available`)

---

## 3. Cart Management

### `POST /api/v1/carts`
Initialize a new temporary shopping cart.

### `GET /api/v1/carts/{cart_id}`
Retrieve current cart state and item details.

### `POST /api/v1/carts/{cart_id}/items`
Add an item variant to cart.

### `PATCH /api/v1/carts/{cart_id}/items/{item_id}`
Update item quantity in cart.

### `DELETE /api/v1/carts/{cart_id}/items/{item_id}`
Remove a specific item from cart.

### `DELETE /api/v1/carts/{cart_id}/items`
Clear all items from cart while preserving cart identity.

### `POST /api/v1/carts/{cart_id}/preview`
Preview cart totals, applicable discounts, delivery fee, and grand total.

---

## 4. Orders

### `POST /api/v1/orders`
Place a customer order from an active cart.

- **Request Body**:
  ```json
  {
    "cart_id": "uuid-string",
    "customer_name": "Ahmed Khan",
    "phone": "03001234567",
    "delivery_address": "House 1, Street 2, F-7",
    "city": "Islamabad",
    "explicit_confirmation": true
  }
  ```
- **Response**: `201 Created` — `OrderView` (`order_number`, `status`, `grand_total`)
