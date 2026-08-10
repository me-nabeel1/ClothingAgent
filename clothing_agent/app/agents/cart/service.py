"""Conversational cart behavior."""

from __future__ import annotations

import re

from app.agents.schemas import AgentRequest, AgentResult
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import (
    AddCartItemRequest,
    CartView,
    UpdateCartItemRequest,
)
from app.core.config import AgentConfig
from app.core.errors import DependencyUnavailableError
from app.core.routing import Intent
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import CART_EXTRACTION_PROMPT
from pydantic import BaseModel, Field

ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}


class CartActionExtraction(BaseModel):
    """References extracted from conversational cart commands."""

    displayed_position: int | None = Field(default=None, ge=1)
    cart_item_position: int | None = Field(default=None, ge=1)
    quantity: int = Field(default=1, ge=1, le=10)


class CartAgent:
    """Resolve natural cart commands against displayed products and cart items."""

    def __init__(
        self,
        llm: LLMClient,
        client: ClothingAppClient,
        config: AgentConfig,
    ) -> None:
        self._llm = llm
        self._client = client
        self._config = config

    async def handle(self, request: AgentRequest) -> AgentResult:
        """Create/view/update/remove/clear cart through application APIs."""

        cart_id = request.context.cart_id
        if request.route.intent == Intent.CART_VIEW:
            if cart_id is None:
                cart = await self._client.create_cart()
                assert isinstance(cart, CartView)
                return AgentResult(
                    reply="Your cart is empty.",
                    cart=cart,
                    ui_actions=["OPEN_CART"],
                    state_updates={"cart_id": cart.cart_id},
                )
            cart = await self._client.get_cart(cart_id)
            assert isinstance(cart, CartView)
            return AgentResult(reply=self._cart_summary(cart), cart=cart, ui_actions=["OPEN_CART"])

        extraction = await self._extract(request)

        if request.route.intent == Intent.CART_ADD:
            displayed = request.context.displayed_products
            position = extraction.displayed_position
            if position is None and len(displayed) == 1:
                position = 1
            selected = next((item for item in displayed if item.position == position), None)
            if not selected:
                return AgentResult(
                    reply="Which displayed product should I add? You can say ‘add the first one’."
                )
            if cart_id is None:
                cart = await self._client.create_cart()
                assert isinstance(cart, CartView)
                cart_id = cart.cart_id
            cart = await self._client.add_cart_item(
                cart_id,
                AddCartItemRequest(
                    variant_id=selected.variant_id,
                    branch_id=selected.branch_id,
                    quantity=extraction.quantity,
                ),
            )
            assert isinstance(cart, CartView)
            return AgentResult(
                reply=f"Added {extraction.quantity} × {selected.product_name} to your cart.",
                cart=cart,
                ui_actions=["OPEN_CART"],
                state_updates={"cart_id": cart.cart_id},
                suggested_actions=["View my cart", "Continue shopping"],
            )

        if cart_id is None:
            return AgentResult(reply="Your cart is empty.")
        cart = await self._client.get_cart(cart_id)
        assert isinstance(cart, CartView)

        if request.route.intent == Intent.CART_CLEAR:
            cleared = await self._client.clear_cart(cart_id)
            assert isinstance(cleared, CartView)
            return AgentResult(reply="Your cart is now empty.", cart=cleared)

        position = extraction.cart_item_position or extraction.displayed_position
        if position is None and len(cart.items) == 1:
            position = 1
        item = cart.items[position - 1] if position and 0 < position <= len(cart.items) else None
        if not item:
            return AgentResult(reply="Which cart item do you mean? Please give its position or name.", cart=cart)

        if request.route.intent == Intent.CART_UPDATE:
            updated = await self._client.update_cart_item(
                cart_id,
                item.item_id,
                UpdateCartItemRequest(quantity=extraction.quantity),
            )
            assert isinstance(updated, CartView)
            return AgentResult(
                reply=f"Updated {item.product_name} to quantity {extraction.quantity}.",
                cart=updated,
            )

        if request.route.intent == Intent.CART_REMOVE:
            updated = await self._client.remove_cart_item(cart_id, item.item_id)
            assert isinstance(updated, CartView)
            return AgentResult(reply=f"Removed {item.product_name} from your cart.", cart=updated)

        return AgentResult(reply=self._cart_summary(cart), cart=cart, ui_actions=["OPEN_CART"])

    async def _extract(self, request: AgentRequest) -> CartActionExtraction:
        """Extract positions and quantity with a deterministic fallback."""

        if self._llm.configured:
            try:
                messages = [LLMMessage(role="system", content=CART_EXTRACTION_PROMPT)]
                for msg in request.context.messages[-self._config.recent_message_limit :]:
                    messages.append(LLMMessage(role=msg.role, content=msg.content))
                return await self._llm.generate_structured(
                    messages,
                    CartActionExtraction,
                )
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise
        text = request.message.lower()
        position = next((value for word, value in ORDINALS.items() if word in text), None)
        option_match = re.search(r"(?:option|item|number)\s*(\d+)", text)
        if option_match:
            position = int(option_match.group(1))
        quantity_match = re.search(r"(?:quantity|qty|to|add)\s*(\d+)", text)
        quantity = int(quantity_match.group(1)) if quantity_match else 1
        return CartActionExtraction(
            displayed_position=position,
            cart_item_position=position,
            quantity=max(1, min(quantity, 10)),
        )

    @staticmethod
    def _cart_summary(cart: CartView) -> str:
        """Build a concise cart summary."""

        if not cart.items:
            return "Your cart is empty."
        return (
            f"Your cart has {cart.total_quantity} item(s) with a subtotal of "
            f"PKR {cart.subtotal}."
        )
