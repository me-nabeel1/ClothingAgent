"""Structured conversation state that incrementally tracks customer preferences."""

from __future__ import annotations

from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.clients.clothing_app.schemas import ProductView, CartItemView


class Budget(BaseModel):
    minimum: Optional[float] = None
    maximum: Optional[float] = None


class ProductInterest(BaseModel):
    """Tracks a product requested by the customer, even if currently unavailable."""
    article_code: Optional[str] = None
    product_name: Optional[str] = None
    requested_color: Optional[str] = None
    requested_size: Optional[str] = None


class CartItemContext(BaseModel):
    """An item currently in the cart."""
    item_id: str
    product_name: str
    color: str
    size: str
    quantity: int
    price: float


class CartContext(BaseModel):
    """Tracks the state of the active cart."""
    cart_id: Optional[UUID] = None
    item_count: int = 0
    subtotal: float = 0.0
    items: list[CartItemContext] = Field(default_factory=list)


class DeliveryContext(BaseModel):
    """Tracks the collected delivery information."""
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    delivery_address: Optional[str] = None
    city: Optional[str] = None
    delivery_notes: Optional[str] = None

    def is_complete(self) -> bool:
        return all([self.customer_name, self.phone, self.delivery_address, self.city])


class DisplayedProduct(BaseModel):
    """A product recently shown to the customer."""
    product_id: int
    article_code: str
    product_name: str
    price: float = 0.0
    available_colors: list[str] = Field(default_factory=list)
    available_sizes: list[str] = Field(default_factory=list)

    def to_product_card(self) -> ProductCard:
        from decimal import Decimal
        pv = ProductView(
            product_id=self.product_id,
            article_code=self.article_code,
            product_name=self.product_name,
            description="",
            category="Men",
            subcategory="",
            product_type="Clothing",
            gender="Men",
            brand="Northstar Menswear",
            material="",
            fit="",
            season="",
            occasion="",
            base_price=Decimal(str(self.price)),
            final_price=Decimal(str(self.price)),
            discount_amount=Decimal("0.00"),
            applied_offer=None,
            images=[],
            variants=[]
        )
        return ProductCard(product=pv)


class ProductCard(BaseModel):
    """Full, ready-to-render product data. Must be the SAME rich object
    type the /products/{id} detail endpoint returns — not a trimmed-down
    summary — so the frontend never needs a follow-up fetch."""
    product: ProductView


class CartCard(BaseModel):
    """Exact, backend-computed cart contents. This becomes the SINGLE
    source of truth for both the chat-feed cart card and the persistent
    cart drawer in the UI — replacing Bug B's dual-source problem."""
    cart_id: str | None = None
    items: list[CartItemView] = Field(default_factory=list)
    item_count: int = 0
    subtotal: float = 0.0


class CheckoutCard(BaseModel):
    """Exact checkout preview numbers. Fixes Bug A — replaces the broken
    text-marker-based parsing entirely."""
    subtotal: float
    discount_total: float = 0.0
    delivery_fee: float = 0.0
    total_amount: float
    applied_offers: list[str] = Field(default_factory=list)


class OrderCard(BaseModel):
    order_number: str
    total_amount: float
    estimated_delivery_days: str = "5-7"


class ConversationState(BaseModel):
    """State containing semantic customer preferences and session data."""
    
    session_id: str
    conversation_stage: str = "greeting"
    current_intent: Optional[str] = None
    message_history: list[dict] = Field(default_factory=list)

    # Shopping preferences
    categories: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    seasons: list[str] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    branch_preference: Optional[str] = None
    
    # Size preferences mapped conceptually (e.g., {"shirt": "L", "pants": "34"})
    size_preferences: dict[str, str] = Field(default_factory=dict)
    
    # Specific product context
    displayed_products: list[DisplayedProduct] = Field(default_factory=list)
    selected_product_id: Optional[int] = None
    requested_unavailable_products: list[ProductInterest] = Field(default_factory=list)
    
    # Cart and checkout context
    cart: CartContext = Field(default_factory=CartContext)
    delivery: DeliveryContext = Field(default_factory=DeliveryContext)
    order_confirmed: bool = False
    
    # Track products shown in this session to prevent repetition when asking for "more"
    seen_product_ids: set[int] = Field(default_factory=set)
    
    # Temporary search overrides for the current request
    current_search: dict[str, Any] = Field(default_factory=dict)
    
    product_cards: list[ProductCard] = Field(default_factory=list)
    cart_card: CartCard | None = None
    checkout_card: CheckoutCard | None = None
    order_card: OrderCard | None = None

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
            "preferred_colors", "excluded_colors", "materials", "fits", "seasons"
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
            
        if "delivery" in delta and delta["delivery"]:
            del_delta = delta["delivery"]
            if "customer_name" in del_delta and del_delta["customer_name"]:
                self.delivery.customer_name = del_delta["customer_name"]
            if "phone" in del_delta and del_delta["phone"]:
                self.delivery.phone = del_delta["phone"]
            if "delivery_address" in del_delta and del_delta["delivery_address"]:
                self.delivery.delivery_address = del_delta["delivery_address"]
            if "city" in del_delta and del_delta["city"]:
                self.delivery.city = del_delta["city"]
            if "delivery_notes" in del_delta and del_delta["delivery_notes"]:
                self.delivery.delivery_notes = del_delta["delivery_notes"]
                
        if "order_confirmed" in delta:
            self.order_confirmed = delta["order_confirmed"]
            
    def record_displayed_products(self, products: list[Any]) -> None:
        """Record products recently shown to the customer."""
        self.displayed_products = []
        for p in products:
            available_colors = set()
            available_sizes = set()
            if hasattr(p, "variants") and p.variants:
                for v in p.variants:
                    if v.is_available:
                        available_colors.add(v.color)
                        available_sizes.add(v.size)
                        
            self.displayed_products.append(
                DisplayedProduct(
                    product_id=p.product_id,
                    article_code=p.article_code,
                    product_name=p.product_name,
                    price=float(p.final_price) if hasattr(p, 'final_price') else 0.0,
                    available_colors=list(available_colors),
                    available_sizes=list(available_sizes)
                )
            )
            self.seen_product_ids.add(p.product_id)
        
    def clear_search_preferences(self) -> None:
        """Clear ephemeral search constraints (useful after switching topics)."""
        self.categories.clear()
        self.occasions.clear()
        self.product_types.clear()
        self.preferred_colors.clear()
        self.materials.clear()
        self.fits.clear()
        self.seasons.clear()
        self.budget = Budget()
        self.selected_product_id = None
        self.current_search.clear()
        self.seen_product_ids.clear()
        self.product_cards = []

    def clear_cards(self) -> None:
        """Reset all card fields. Call this at the start of every
        card-producing tool call so state never carries a stale card from
        a previous, unrelated turn."""
        self.product_cards = []
        self.cart_card = None
        self.checkout_card = None
        self.order_card = None

    def filter_displayed_cards(self, indices: list[int]) -> None:
        """Filter displayed products and cards to only the 1-based indices specified."""
        if not indices or not self.displayed_products:
            return
        valid_indices = [i for i in indices if 1 <= i <= len(self.displayed_products)]
        if not valid_indices:
            return
        
        selected_displayed = [self.displayed_products[i - 1] for i in valid_indices]
        self.displayed_products = selected_displayed
        
        selected_ids = {dp.product_id for dp in selected_displayed}
        if self.product_cards:
            filtered = [c for c in self.product_cards if c.product.product_id in selected_ids]
            if filtered:
                self.product_cards = filtered
            else:
                self.product_cards = [dp.to_product_card() for dp in selected_displayed]
        else:
            self.product_cards = [dp.to_product_card() for dp in selected_displayed]
            
        if len(selected_displayed) == 1:
            self.selected_product_id = selected_displayed[0].product_id
    
    session_id: str
    conversation_stage: str = "greeting"
    current_intent: Optional[str] = None
    message_history: list[dict] = Field(default_factory=list)

    # Shopping preferences
    categories: list[str] = Field(default_factory=list)
    occasions: list[str] = Field(default_factory=list)
    product_types: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    seasons: list[str] = Field(default_factory=list)
    budget: Budget = Field(default_factory=Budget)
    branch_preference: Optional[str] = None
    
    # Size preferences mapped conceptually (e.g., {"shirt": "L", "pants": "34"})
    size_preferences: dict[str, str] = Field(default_factory=dict)
    
    # Specific product context
    displayed_products: list[DisplayedProduct] = Field(default_factory=list)
    selected_product_id: Optional[int] = None
    requested_unavailable_products: list[ProductInterest] = Field(default_factory=list)
    
    # Cart and checkout context
    cart: CartContext = Field(default_factory=CartContext)
    delivery: DeliveryContext = Field(default_factory=DeliveryContext)
    order_confirmed: bool = False
    
    # Track products shown in this session to prevent repetition when asking for "more"
    seen_product_ids: set[int] = Field(default_factory=set)
    
    # Temporary search overrides for the current request
    current_search: dict[str, Any] = Field(default_factory=dict)
    
    product_cards: list[ProductCard] = Field(default_factory=list)
    cart_card: CartCard | None = None
    checkout_card: CheckoutCard | None = None
    order_card: OrderCard | None = None

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
            "preferred_colors", "excluded_colors", "materials", "fits", "seasons"
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
            
        if "delivery" in delta and delta["delivery"]:
            del_delta = delta["delivery"]
            if "customer_name" in del_delta and del_delta["customer_name"]:
                self.delivery.customer_name = del_delta["customer_name"]
            if "phone" in del_delta and del_delta["phone"]:
                self.delivery.phone = del_delta["phone"]
            if "delivery_address" in del_delta and del_delta["delivery_address"]:
                self.delivery.delivery_address = del_delta["delivery_address"]
            if "city" in del_delta and del_delta["city"]:
                self.delivery.city = del_delta["city"]
            if "delivery_notes" in del_delta and del_delta["delivery_notes"]:
                self.delivery.delivery_notes = del_delta["delivery_notes"]
                
        if "order_confirmed" in delta:
            self.order_confirmed = delta["order_confirmed"]
            
    def record_displayed_products(self, products: list[Any]) -> None:
        """Record products recently shown to the customer."""
        self.displayed_products = []
        for p in products:
            available_colors = set()
            available_sizes = set()
            if hasattr(p, "variants") and p.variants:
                for v in p.variants:
                    if v.is_available:
                        available_colors.add(v.color)
                        available_sizes.add(v.size)
                        
            self.displayed_products.append(
                DisplayedProduct(
                    product_id=p.product_id,
                    article_code=p.article_code,
                    product_name=p.product_name,
                    price=float(p.final_price) if hasattr(p, 'final_price') else 0.0,
                    available_colors=list(available_colors),
                    available_sizes=list(available_sizes)
                )
            )
            self.seen_product_ids.add(p.product_id)
        
    def clear_search_preferences(self) -> None:
        """Clear ephemeral search constraints (useful after switching topics)."""
        self.categories.clear()
        self.occasions.clear()
        self.product_types.clear()
        self.preferred_colors.clear()
        self.materials.clear()
        self.fits.clear()
        self.seasons.clear()
        self.budget = Budget()
        self.selected_product_id = None
        self.current_search.clear()
        self.seen_product_ids.clear()
        self.product_cards = []

    def clear_cards(self) -> None:
        """Reset all card fields. Call this at the start of every
        card-producing tool call so state never carries a stale card from
        a previous, unrelated turn."""
        self.product_cards = []
        self.cart_card = None
        self.checkout_card = None
        self.order_card = None

    def reset(self, keep_cart: bool = False) -> None:
        """Flush session preferences, stage, and message history while retaining active cart items if keep_cart=True."""
        existing_cart = self.cart if keep_cart else CartContext()
        self.conversation_stage = "greeting"
        self.current_intent = None
        self.message_history.clear()

        self.categories.clear()
        self.occasions.clear()
        self.product_types.clear()
        self.preferred_colors.clear()
        self.excluded_colors.clear()
        self.materials.clear()
        self.fits.clear()
        self.seasons.clear()
        self.budget = Budget()
        self.branch_preference = None
        self.size_preferences.clear()

        self.displayed_products.clear()
        self.selected_product_id = None
        self.requested_unavailable_products.clear()

        self.cart = existing_cart
        self.delivery = DeliveryContext()
        self.order_confirmed = False

        self.seen_product_ids.clear()
        self.current_search.clear()

        self.clear_cards()

    def filter_displayed_cards(self, indices: list[int]) -> None:
        """Filter displayed products and cards to only the 1-based indices specified."""
        if not indices or not self.displayed_products:
            return
        valid_indices = [i for i in indices if 1 <= i <= len(self.displayed_products)]
        if not valid_indices:
            return
        
        selected_displayed = [self.displayed_products[i - 1] for i in valid_indices]
        self.displayed_products = selected_displayed
        
        selected_ids = {dp.product_id for dp in selected_displayed}
        if self.product_cards:
            filtered = [c for c in self.product_cards if c.product.product_id in selected_ids]
            if filtered:
                self.product_cards = filtered
            else:
                self.product_cards = [dp.to_product_card() for dp in selected_displayed]
        else:
            self.product_cards = [dp.to_product_card() for dp in selected_displayed]
            
        if len(selected_displayed) == 1:
            self.selected_product_id = selected_displayed[0].product_id

    def sync_displayed_products_with_reply(self, reply: str) -> None:
        """Sync displayed_products and product_cards so cards are ONLY displayed during search/discovery turns for products described in reply text. Suppress cards during detail queries, follow-up turns, greetings, general store chat, and variant requests."""
        if not self.displayed_products or self.current_intent in ["general_chat", "greeting", "general_inquiry", "store_overview", "faq", "general", "clear_preferences", "reset_session", "get_promotions", None]:
            self.product_cards = []
            self.displayed_products = []
            return

        import re
        reply_lower = reply.lower()

        def normalize(text: str) -> str:
            if not text:
                return ""
            cleaned = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015\-_\.]', ' ', text)
            cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
            return " ".join(cleaned.lower().split())

        norm_reply = normalize(reply)

        matched_products = []
        for dp in self.displayed_products:
            is_matched = False

            if dp.article_code and dp.article_code.lower() in reply_lower:
                is_matched = True

            norm_name = normalize(dp.product_name)
            if norm_name and norm_name in norm_reply:
                is_matched = True

            if not is_matched and norm_name:
                words = norm_name.split()
                if len(words) >= 2:
                    non_generic = [w for w in words if w not in {"shirt", "t", "tee", "pants", "trouser", "jacket", "hoodie", "men", "mens"}]
                    if non_generic and all(w in norm_reply for w in non_generic):
                        is_matched = True

            if is_matched:
                matched_products.append(dp)

        if not matched_products:
            option_matches = re.findall(r'(?:Option|اپشن|آپشن|نمبر|\b)\s*([1-9])\b[\s\.\:\-–\)]', reply, re.IGNORECASE)
            if option_matches:
                indices = []
                for m in option_matches:
                    idx = int(m)
                    if 1 <= idx <= len(self.displayed_products) and idx not in indices:
                        indices.append(idx)
                if indices:
                    matched_products = [self.displayed_products[i - 1] for i in indices]

        if matched_products:
            self.displayed_products = matched_products

        matched_ids = {dp.product_id for dp in self.displayed_products}

        # Product cards handling:
        if self.current_intent in ["show_cart", "remove_cart", "add_to_cart", "get_details"]:
            # For cart and detail operations, preserve the exact product_cards set by the tool
            if not self.product_cards and self.displayed_products:
                self.product_cards = [dp.to_product_card() for dp in self.displayed_products]
        elif self.current_intent in ["search", "explore_category"] and self.displayed_products:
            if self.product_cards:
                if matched_ids:
                    filtered_cards = [c for c in self.product_cards if c.product.product_id in matched_ids]
                    if filtered_cards:
                        self.product_cards = filtered_cards
            else:
                self.product_cards = [dp.to_product_card() for dp in self.displayed_products]
        else:
            self.product_cards = []
            self.displayed_products = []
