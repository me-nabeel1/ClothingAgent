from pydantic import BaseModel, Field
from typing import Optional, Any
from uuid import UUID
import json

class Budget(BaseModel):
    minimum: Optional[float] = None
    maximum: Optional[float] = None

class SearchProductsPayload(BaseModel):
    """Search for products based on specific criteria."""
    search_query: Optional[str] = Field(None, description="Free text semantic search if specific vocabulary doesn't match")
    categories: Optional[list[str]] = Field(None)
    product_types: Optional[list[str]] = Field(None)
    occasions: Optional[list[str]] = Field(None)
    colors: Optional[list[str]] = Field(None)
    excluded_colors: Optional[list[str]] = Field(None)
    sizes: Optional[dict[str, str]] = Field(None, description="e.g. {'shirt': 'L', 'pants': '34'}")
    materials: Optional[list[str]] = Field(None)
    fits: Optional[list[str]] = Field(None)
    seasons: Optional[list[str]] = Field(None)
    budget: Optional[Budget] = Field(None)
    branch: Optional[str] = None
    specific_article: Optional[str] = Field(None, description="Exact article code if mentioned (e.g., NS-SH-001)")
    clear_previous_preferences: bool = Field(False, description="Set to true if the user is completely changing the topic or abandoning a previous search.")

class GetProductDetailsPayload(BaseModel):
    """Get rich details for a specific product."""
    product_id: Optional[int] = Field(None, description="The ID of the product if known")
    selected_product_index: Optional[int] = Field(None, description="1-based index of product if user is referring to a recently displayed product list")

class AddCartItemPayload(BaseModel):
    """Add a specific item variant to the cart. DO NOT call this tool unless the user has explicitly specified BOTH color and size. If color or size is missing, ask the user to clarify their color and size preference first or call get_product_details."""
    product_id: Optional[int] = Field(None, description="The ID of the product if known")
    selected_product_index: Optional[int] = Field(None, description="1-based index of product if user is referring to a recently displayed product list")
    color: Optional[str] = Field(None, description="The explicitly chosen color for the item. DO NOT GUESS or infer from history.")
    size: Optional[str] = Field(None, description="The explicitly chosen size for the item. DO NOT GUESS or infer from history.")
    quantity: int = Field(1, description="Quantity to add")

class UpdateCartItemPayload(BaseModel):
    """Update the quantity of an item in the cart."""
    item_index: Optional[int] = Field(None, description="The 1-based index of the item in the cart to update.")
    product_name: Optional[str] = Field(None, description="The name of the product to update.")
    new_quantity: int = Field(..., ge=1, description="The new quantity (must be at least 1).")

class ClearCartPayload(BaseModel):
    """Clear all items from the cart."""
    pass

class CheckAvailabilityPayload(BaseModel):
    """Check availability of a specific product variant."""
    product_id: int = Field(..., description="The ID of the product.")
    color: Optional[str] = Field(None, description="The specific color.")
    size: Optional[str] = Field(None, description="The specific size.")
    branch: Optional[str] = Field(None, description="The branch name to check.")

class GetOrderStatusPayload(BaseModel):
    """Retrieve the status of an existing order."""
    order_id: UUID = Field(..., description="The order ID to look up.")

class PreviewCheckoutPayload(BaseModel):
    """Preview the checkout total and get ready to ask for delivery info."""
    pass

class ShowCartPayload(BaseModel):
    """Show the current items in the cart to the user."""
    pass

class RemoveCartItemPayload(BaseModel):
    """Remove a specific item from the cart."""
    item_index: Optional[int] = Field(None, description="1-based index of the item in the cart to remove.")
    product_name: Optional[str] = Field(None, description="Name of the product to remove if index is not known.")

class PlaceOrderPayload(BaseModel):
    """Place an order with the user's delivery details."""
    customer_name: str
    phone: str
    delivery_address: str
    city: str
    delivery_notes: Optional[str] = None

class GetPromotionsPayload(BaseModel):
    """Fetch active promotions and offers."""
    pass

class ExploreCategoryPayload(BaseModel):
    """Explore a specific product category (e.g., 'T-Shirts', 'Shirts', 'Pants', 'Outerwear', 'Traditional', 'Trousers'). Returns 2-3 featured products and available subcategories/styles within that category."""
    category_name: str = Field(..., description="The category the user wants to explore (e.g., 'T-Shirts', 'Shirts', 'Pants')")

def clean_schema(model: type[BaseModel]) -> dict[str, Any]:
    schema = model.model_json_schema()
    def remove_titles(obj: Any) -> None:
        if isinstance(obj, dict):
            obj.pop("title", None)
            for v in obj.values():
                remove_titles(v)
        elif isinstance(obj, list):
            for item in obj:
                remove_titles(item)
    remove_titles(schema)
    return schema

tools = [
    {"type": "function", "function": {"name": "explore_category", "description": ExploreCategoryPayload.__doc__, "parameters": clean_schema(ExploreCategoryPayload)}},
    {"type": "function", "function": {"name": "search_products", "description": SearchProductsPayload.__doc__, "parameters": clean_schema(SearchProductsPayload)}},
    {"type": "function", "function": {"name": "get_product_details", "description": GetProductDetailsPayload.__doc__, "parameters": clean_schema(GetProductDetailsPayload)}},
    {"type": "function", "function": {"name": "add_cart_item", "description": AddCartItemPayload.__doc__, "parameters": clean_schema(AddCartItemPayload)}},
    {"type": "function", "function": {"name": "remove_cart_item", "description": RemoveCartItemPayload.__doc__, "parameters": clean_schema(RemoveCartItemPayload)}},
    {"type": "function", "function": {"name": "show_cart", "description": ShowCartPayload.__doc__, "parameters": clean_schema(ShowCartPayload)}},
    {"type": "function", "function": {"name": "preview_checkout", "description": PreviewCheckoutPayload.__doc__, "parameters": clean_schema(PreviewCheckoutPayload)}},
    {"type": "function", "function": {"name": "place_order", "description": PlaceOrderPayload.__doc__, "parameters": clean_schema(PlaceOrderPayload)}},
    {"type": "function", "function": {"name": "get_promotions", "description": GetPromotionsPayload.__doc__, "parameters": clean_schema(GetPromotionsPayload)}},
]
