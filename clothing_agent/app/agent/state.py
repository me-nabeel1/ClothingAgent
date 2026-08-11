"""Structured conversation state that incrementally tracks customer preferences."""

from __future__ import annotations

from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field


class Budget(BaseModel):
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class ProductInterest(BaseModel):
    """Tracks a product requested by the customer, even if currently unavailable."""
    article_code: Optional[str] = None
    product_name: Optional[str] = None
    requested_color: Optional[str] = None
    requested_size: Optional[str] = None


class CartContext(BaseModel):
    """Tracks the state of the active cart."""
    cart_id: Optional[UUID] = None
    item_count: int = 0
    subtotal: float = 0.0


class DisplayedProduct(BaseModel):
    """A product recently shown to the customer."""
    product_id: int
    article_code: str
    product_name: str


class ConversationState(BaseModel):
    """State containing semantic customer preferences and session data."""
    
    session_id: str
    conversation_stage: str = "greeting"
    current_intent: Optional[str] = None

    # Shopping preferences
    categories: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    branch_preference: Optional[str] = None
    
    # Size preferences mapped conceptually (e.g., {"shirt": "L", "pants": "34"})
    size_preferences: dict[str, str] = Field(default_factory=dict)
    
    # Specific product context
    displayed_products: list[DisplayedProduct] = Field(default_factory=list)
    selected_product_id: Optional[int] = None
    requested_unavailable_products: list[ProductInterest] = Field(default_factory=list)
    
    # Cart context
    cart: CartContext = Field(default_factory=CartContext)
    
    # Temporary search overrides for the current request
    current_search: dict[str, Any] = Field(default_factory=dict)

    def update(self, delta: dict[str, Any]) -> None:
        """Incrementally update state fields using a delta dictionary."""
        
        if "conversation_stage" in delta and delta["conversation_stage"]:
            self.conversation_stage = delta["conversation_stage"]
            
        if "current_intent" in delta and delta["current_intent"]:
            self.current_intent = delta["current_intent"]

        # For lists, replace if new ones are provided explicitly.
        # Alternatively, if we wanted merging, we could extend.
        # The prompt implies: "Actually make it blue. State -> colors = [blue]".
        # So explicit replacement of the list is correct when the user changes preferences.
        for list_field in [
            "categories", "occasions", "product_types", 
            "preferred_colors", "excluded_colors", "materials", "fits"
        ]:
            if list_field in delta and delta[list_field] is not None:
                # If an empty list is passed in the delta, it effectively clears it.
                setattr(self, list_field, delta[list_field])
                
        if "budget" in delta and delta["budget"]:
            budget_delta = delta["budget"]
            if "minimum" in budget_delta and budget_delta["minimum"] is not None:
                self.budget.minimum = budget_delta["minimum"]
            if "maximum" in budget_delta and budget_delta["maximum"] is not None:
                self.budget.maximum = budget_delta["maximum"]

        if "branch_preference" in delta and delta["branch_preference"]:
            self.branch_preference = delta["branch_preference"]

        if "size_preferences" in delta and delta["size_preferences"]:
            # Update dictionary incrementally
            for k, v in delta["size_preferences"].items():
                self.size_preferences[k] = v

        if "selected_product_id" in delta:
            self.selected_product_id = delta["selected_product_id"]
            
    def record_displayed_products(self, products: list[Any]) -> None:
        """Record products recently shown to the customer."""
        self.displayed_products = [
            DisplayedProduct(
                product_id=p.product_id,
                article_code=p.article_code,
                product_name=p.product_name
            ) for p in products
        ]
        
    def clear_search_preferences(self) -> None:
        """Clear ephemeral search constraints (useful after switching topics)."""
        self.categories.clear()
        self.occasions.clear()
        self.product_types.clear()
        self.preferred_colors.clear()
        self.materials.clear()
        self.fits.clear()
        self.budget = Budget()
        self.selected_product_id = None
        self.current_search.clear()
