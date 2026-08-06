"""Guided product discovery, selection, details, and availability behavior."""

from __future__ import annotations

import json
import logging
import re
from decimal import Decimal

from pydantic import BaseModel, Field

from app.agents.schemas import AgentRequest, AgentResult
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import (
    AvailabilityView,
    BranchView,
    ProductDetails,
    ProductOption,
    ProductSearchRequest,
    ProductSearchResponse,
)
from app.core.config import AgentConfig
from app.core.conversation import ConversationState, DisplayedProduct, ShoppingPreferences
from app.core.errors import AgentError, DependencyUnavailableError
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SEARCH_EXTRACTION_PROMPT, SHOPPING_RESPONSE_PROMPT
from app.core.routing import Intent

COLORS = {
    "black", "white", "blue", "navy", "red", "green", "beige", "brown",
    "grey", "gray", "charcoal", "khaki", "olive", "maroon", "pink",
}
CATEGORIES = {
    "shirt": "shirts", "shirts": "shirts", "trouser": "trousers",
    "trousers": "trousers", "pants": "pants", "pant": "pants", "jeans": "jeans",
    "shorts": "shorts", "tee": "t-shirts", "tshirt": "t-shirts",
    "t-shirt": "t-shirts", "hoodie": "hoodies", "jacket": "jackets",
    "activewear": "active wear", "gymwear": "active wear",
    "pajama": "pajamas", "pajamas": "pajamas", "sweatpants": "sweatpants",
    "jogger": "joggers", "joggers": "joggers", "sweater": "sweaters",
    "sweaters": "sweaters", "coat": "coats", "coats": "coats"
}
UPPER_BODY_CATEGORIES = {"shirts", "t-shirts", "hoodies", "jackets", "sweaters", "coats"}
LOWER_BODY_CATEGORIES = {"trousers", "pants", "jeans", "shorts", "active wear", "pajamas", "sweatpants", "joggers"}
PURPOSES = {
    "casual": "casual", "everyday": "everyday", "office": "office",
    "formal": "formal", "gym": "gym", "workout": "gym",
    "activewear": "activewear", "travel": "travel", "wedding": "wedding",
    "party": "party", "dinner": "dinner",
}
FITS = {"relaxed", "regular", "slim", "fitted", "oversized", "loose"}
MATERIALS = {"cotton", "linen", "polyester", "denim", "fleece"}
SEMANTIC_TAGS = {
    "comfortable", "breathable", "summer", "travel", "formal", "office",
    "gym", "lightweight", "casual", "everyday", "winter", "smart",
}
ORDINALS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5}
BRANCH_HINTS = {"branch", "store", "lahore", "karachi", "islamabad", "gulberg", "dha", "blue area"}
logger = logging.getLogger(__name__)
audit = logging.getLogger("sales_audit")


class ProductSearchExtraction(BaseModel):
    """Product constraints extracted from one customer turn."""

    query_text: str | None = None
    category: str | None = None
    purpose: str | None = None
    occasion: str | None = None
    colors: list[str] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    minimum_price: Decimal | None = None
    maximum_price: Decimal | None = None
    branch_code: str | None = None
    materials: list[str] = Field(default_factory=list)
    fits: list[str] = Field(default_factory=list)
    semantic_tags: list[str] = Field(default_factory=list)
    in_stock_only: bool = True


class ShoppingAgent:
    """Guide discovery and call clothing-app APIs only when ready to search."""

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
        """Continue guided discovery or execute a grounded product operation."""

        if request.route.intent == Intent.PRODUCT_SELECTION:
            return await self._select_product(request)
        if request.route.intent == Intent.FIND_SIMILAR:
            return await self._find_similar(request)
        if request.route.intent == Intent.PRODUCT_DETAILS:
            return await self._show_details(request)
        if request.route.intent == Intent.AVAILABILITY_CHECK:
            return await self._check_availability(request)

        extraction = await self._extract(request)
        preferences = self._merge_preferences(request.context.preferences, extraction)
        clarification = self._next_clarification(
            preferences,
            request.context.clarification_count,
            request.message,
        )
        if clarification and request.context.clarification_count < self._config.maximum_clarification_questions:
            question, actions = clarification
            audit.info(
                "clarification_asked",
                extra={
                    "event": "clarification_asked",
                    "conversation_id": str(request.context.conversation_id),
                    "clarification_count": request.context.clarification_count + 1,
                    "category": preferences.category,
                },
            )
            return AgentResult(
                reply=question,
                suggested_actions=actions,
                state_updates={
                    "preferences": preferences,
                    "shopping_stage": "clarifying",
                    "clarification_count": request.context.clarification_count + 1,
                },
            )

        normalized = await self._normalize_branch(preferences, request.message)
        search_request = self._to_search_request(normalized)
        audit.info(
            "inventory_search_started",
            extra={
                "event": "inventory_search_started",
                "conversation_id": str(request.context.conversation_id),
                "filters": search_request.model_dump(mode="json"),
            },
        )
        result = await self._client.search_products(search_request)
        
        if not result.products:
            fallback_category = None
            if search_request.category:
                if search_request.category in LOWER_BODY_CATEGORIES:
                    fallback_category = "trousers"
                elif search_request.category in UPPER_BODY_CATEGORIES:
                    fallback_category = "t-shirts"
                    
            fallback_request = ProductSearchRequest(
                limit=self._config.displayed_product_limit,
                category=fallback_category
            )
            fallback_result = await self._client.search_products(fallback_request)
            result.products = fallback_result.products
            result.relaxed_constraints.append("fallback_to_alternatives")

        assert isinstance(result, ProductSearchResponse)
        audit.info(
            "inventory_search_completed",
            extra={
                "event": "inventory_search_completed",
                "conversation_id": str(request.context.conversation_id),
                "result_count": result.result_count,
                "displayed_count": min(len(result.products), self._config.displayed_product_limit),
                "relaxed_constraints": result.relaxed_constraints,
            },
        )
        reply = await self._compose_search_reply(request, normalized, result)
        return AgentResult(
            reply=reply,
            products=result.products[: self._config.displayed_product_limit],
            suggested_actions=(
                ["Show option 1 details", "The second one looks better", "Show me a cheaper option"]
                if result.products
                else ["Try another color", "Change the budget", "Choose another style"]
            ),
            state_updates={
                "preferences": normalized,
                "shopping_stage": "presented" if result.products else "ready",
                "clarification_count": 0,
            },
        )

    async def _select_product(self, request: AgentRequest) -> AgentResult:
        """Resolve a conversational reference and remember the selected option."""

        reference = self._resolve_reference(request.message, request.context)
        if not reference:
            return AgentResult(reply="Which option do you like—the first, second, or third?")
        details = await self._client.get_product(reference.product_id)
        assert isinstance(details, ProductDetails)
        option = self._exact_option(details, reference)
        products = [option] if option else []
        return AgentResult(
            reply=(
                f"Good pick—{reference.product_name} in {reference.color}, size {reference.size}, "
                f"is PKR {reference.price}. Want me to check stock or add it to your cart?"
            ),
            products=products,
            suggested_actions=["Check its availability", "Add it to my cart", "Show similar options"],
            state_updates={
                "selected_product": reference,
                "shopping_stage": "selected",
            },
        )

    async def _find_similar(self, request: AgentRequest) -> AgentResult:
        """Find alternatives based on the selected or referenced product."""

        reference = self._resolve_reference(request.message, request.context)
        if not reference:
            return AgentResult(reply="Which displayed option should I use as the reference?")
        details = await self._registry.execute("inventory.product_details", reference.product_id)
        assert isinstance(details, ProductDetails)
        preferences = request.context.preferences.model_copy(deep=True)
        preferences.category = details.category
        if details.material and details.material not in preferences.materials:
            preferences.materials.append(details.material)
        if details.fit and details.fit not in preferences.fits:
            preferences.fits.append(details.fit)
        search_request = self._to_search_request(preferences, limit=self._config.displayed_product_limit + 2)
        result = await self._client.search_products(search_request)
        assert isinstance(result, ProductSearchResponse)
        alternatives = [item for item in result.products if item.product_id != reference.product_id]
        alternatives = alternatives[: self._config.displayed_product_limit]
        if not alternatives:
            return AgentResult(
                reply="I couldn’t find a close in-stock alternative. Should I relax the color or fit?",
                state_updates={"selected_product": reference},
            )
        return AgentResult(
            reply=f"These are the closest alternatives to {reference.product_name}. The first is my strongest match.",
            products=alternatives,
            suggested_actions=["The first one looks good", "Compare with the previous one"],
            state_updates={
                "selected_product": reference,
                "preferences": preferences,
                "shopping_stage": "presented",
            },
        )

    async def _show_details(self, request: AgentRequest) -> AgentResult:
        """Return grounded details for a displayed product reference."""

        reference = self._resolve_reference(request.message, request.context)
        if not reference:
            return AgentResult(reply="Which option would you like to know more about?")
        details = await self._client.get_product(reference.product_id)
        assert isinstance(details, ProductDetails)
        option = self._exact_option(details, reference)
        return AgentResult(
            reply=self._details_reply(details, reference),
            products=[option] if option else [],
            suggested_actions=["Check its availability", "Add it to my cart", "Show similar options"],
            state_updates={"selected_product": reference, "shopping_stage": "selected"},
        )

    async def _check_availability(self, request: AgentRequest) -> AgentResult:
        """Check stock for the selected or referenced exact variant."""

        reference = self._resolve_reference(request.message, request.context)
        if not reference:
            return AgentResult(reply="Which option should I check?")
        availability = await self._client.get_availability(reference.variant_id, reference.branch_id)
        assert isinstance(availability, AvailabilityView)
        if availability.is_available:
            reply = (
                f"Yes—{availability.available_quantity} available at {availability.branch_name} "
                f"in {availability.color}, size {availability.size}."
            )
            actions = ["Add it to my cart", "Show similar options"]
        else:
            reply = f"That exact option is out of stock at {availability.branch_name}."
            actions = ["Show similar options"]
        return AgentResult(
            reply=reply,
            suggested_actions=actions,
            state_updates={"selected_product": reference},
        )

    async def _extract(
        self,
        request: AgentRequest,
    ) -> ProductSearchExtraction:
        """Extract only new preferences from the latest customer turn."""

        if self._llm.configured:
            try:
                messages = [LLMMessage(role="system", content=SEARCH_EXTRACTION_PROMPT)]
                messages.append(
                    LLMMessage(
                        role="system",
                        content=f"Saved preferences: {request.context.preferences.model_dump(mode='json')}",
                    )
                )
                for msg in request.context.messages[-self._config.recent_message_limit :]:
                    messages.append(LLMMessage(role=msg.role, content=msg.content))
                return await self._llm.generate_structured(
                    messages,
                    ProductSearchExtraction,
                )
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise
        return self._heuristic_extract(request.message)

    @staticmethod
    def _heuristic_extract(message: str) -> ProductSearchExtraction:
        """Provide predictable extraction when the LLM is unavailable."""

        text = message.lower()
        category = next((value for key, value in CATEGORIES.items() if key in text), None)
        colors = [color for color in COLORS if re.search(rf"\b{re.escape(color)}\b", text)]
        size_match = re.search(r"(?:size\s*)?\b(\d{2}|xs|s|m|l|xl|xxl)\b", text, re.I)
        price_match = re.search(
            r"(?:under|below|maximum|max|budget)\s*(?:pkr|rs\.?|rupees)?\s*([0-9,]+)",
            text,
        )
        maximum_price = Decimal(price_match.group(1).replace(",", "")) if price_match else None
        purpose = next((value for key, value in PURPOSES.items() if key in text), None)
        occasion = next((key for key in ("wedding", "party", "dinner", "interview", "event") if key in text), None)
        fits = [fit for fit in FITS if re.search(rf"\b{re.escape(fit)}\b", text)]
        materials = [item for item in MATERIALS if item in text]
        tags = [tag for tag in SEMANTIC_TAGS if tag in text]
        return ProductSearchExtraction(
            query_text=message,
            category=category,
            purpose=purpose,
            occasion=occasion,
            colors=colors,
            sizes=[size_match.group(1).upper()] if size_match else [],
            maximum_price=maximum_price,
            materials=materials,
            fits=fits,
            semantic_tags=tags,
        )

    @staticmethod
    def _merge_preferences(
        current: ShoppingPreferences,
        extraction: ProductSearchExtraction,
    ) -> ShoppingPreferences:
        """Merge new facts into saved preferences without losing prior context."""

        merged = current.model_copy(deep=True)
        for field in (
            "category", "purpose", "occasion", "minimum_price",
            "maximum_price", "branch_code",
        ):
            value = getattr(extraction, field)
            if value is not None:
                setattr(merged, field, value)
        for field in ("colors", "sizes", "materials", "fits", "semantic_tags"):
            incoming = getattr(extraction, field)
            if incoming:
                existing = getattr(merged, field)
                setattr(merged, field, list(dict.fromkeys([*existing, *incoming])))
        if merged.purpose and merged.purpose not in merged.semantic_tags:
            merged.semantic_tags.append(merged.purpose)
        if merged.occasion and merged.occasion not in merged.semantic_tags:
            merged.semantic_tags.append(merged.occasion)
        return merged

    def _next_clarification(
        self,
        preferences: ShoppingPreferences,
        count: int,
        message: str,
    ) -> tuple[str, list[str]] | None:
        """Ask only the highest-value question before showing products.

        The agent uses progressive disclosure: once it knows the product type
        and either a purpose or another useful constraint, it shows products.
        Fit, color, and budget can then be refined from visible choices instead
        of creating a long interview before the customer sees value.
        """

        if count >= self._config.maximum_clarification_questions:
            return None
        text = message.lower()
        has_specific_constraint = bool(
            preferences.colors
            or preferences.sizes
            or preferences.maximum_price is not None
            or preferences.materials
            or preferences.fits
            or preferences.branch_code
        )
        if not preferences.category:
            if preferences.occasion or "outfit" in text:
                return (
                    "Let’s narrow it quickly—shirts, trousers, or activewear?",
                    ["Shirts", "Trousers", "Activewear"],
                )
            return (
                "What should I pull first—shirts, trousers, or activewear?",
                ["Shirts", "Trousers", "Activewear"],
            )

        # Ask one purpose question only on the first broad category request.
        # After the customer's answer, show products and refine visually.
        if (
            count == 0
            and not preferences.purpose
            and not preferences.occasion
            and not has_specific_constraint
        ):
            category = preferences.category.lower()
            if "shirt" in category:
                return (
                    "Sure—casual, office/formal, gym, or a specific occasion?",
                    ["Casual", "Office/formal", "Gym", "Special occasion"],
                )
            return (
                "What’s the main use—everyday, office, gym, or an occasion?",
                ["Everyday", "Office", "Gym", "Special occasion"],
            )
        return None

    async def _normalize_branch(
        self,
        preferences: ShoppingPreferences,
        message: str,
    ) -> ShoppingPreferences:
        """Resolve a branch name or city into the application's branch code."""

        requested = (preferences.branch_code or "").strip().lower()
        message_text = message.lower()
        if not requested and not any(hint in message_text for hint in BRANCH_HINTS):
            # Most searches do not need branch discovery. Avoiding this API call
            # removes latency and prevents an unrelated branch failure from
            # blocking otherwise valid product retrieval.
            return preferences
        try:
            branches = await self._client.list_branches()
        except AgentError as exc:
            logger.warning(
                "branch_normalization_skipped",
                extra={
                    "event": "branch_normalization_skipped",
                    "error_code": exc.code,
                },
            )
            preferences.branch_code = None
            return preferences
        assert isinstance(branches, list)
        typed = [item for item in branches if isinstance(item, BranchView)]
        match = next(
            (
                branch for branch in typed
                if (
                    requested and requested in {
                        branch.branch_code.lower(),
                        branch.branch_name.lower(),
                        branch.city.lower(),
                    }
                ) or (
                    not requested and (
                        branch.city.lower() in message_text
                        or branch.branch_name.lower() in message_text
                        or branch.branch_code.lower() in message_text
                    )
                )
            ),
            None,
        )
        if match:
            preferences.branch_code = match.branch_code
        elif requested:
            preferences.branch_code = None
        return preferences

    def _to_search_request(
        self,
        preferences: ShoppingPreferences,
        *,
        limit: int | None = None,
    ) -> ProductSearchRequest:
        """Convert conversation preferences into the clothing-app API contract."""

        summary = " ".join(
            str(value) for value in (
                preferences.category,
                preferences.purpose,
                preferences.occasion,
                " ".join(preferences.semantic_tags),
            ) if value
        )
        return ProductSearchRequest(
            query_text=summary or None,
            category=preferences.category,
            colors=preferences.colors,
            sizes=preferences.sizes,
            minimum_price=preferences.minimum_price,
            maximum_price=preferences.maximum_price,
            branch_code=preferences.branch_code,
            materials=preferences.materials,
            fits=preferences.fits,
            semantic_tags=preferences.semantic_tags,
            in_stock_only=True,
            allow_relaxation=True,
            limit=limit or self._config.displayed_product_limit,
        )

    async def _compose_search_reply(
        self,
        request: AgentRequest,
        preferences: ShoppingPreferences,
        result: ProductSearchResponse,
    ) -> str:
        """Generate a short grounded sales response."""

        if self._llm.configured:
            try:
                messages = [LLMMessage(role="system", content=SHOPPING_RESPONSE_PROMPT)]
                for msg in request.context.messages[-self._config.recent_message_limit :]:
                    messages.append(LLMMessage(role=msg.role, content=msg.content))
                
                system_context = json.dumps({
                    "preferences": preferences.model_dump(mode="json"),
                    "products": [item.model_dump(mode="json") for item in result.products],
                    "relaxed_constraints": result.relaxed_constraints,
                })
                messages.append(LLMMessage(role="system", content=f"Search Results Context: {system_context}"))

                return (
                    await self._llm.generate_text(
                        messages,
                        max_tokens=120,
                    )
                ).strip()
            except DependencyUnavailableError:
                if not self._config.allow_local_fallback:
                    raise
        first = result.products[0]
        reason = (
            first.match_reasons[0].rstrip(".")
            if first.match_reasons
            else next(
                (
                    value
                    for value in (first.material, first.fit, first.season)
                    if value
                ),
                "it is the strongest match for what you described",
            )
        )
        return (
            f"I pulled {min(result.result_count, self._config.displayed_product_limit)} strong in-stock picks. "
            f"Start with {first.product_name}—{reason.lower()}. Take a look and tell me which one catches your eye."
        )

    @staticmethod
    def _resolve_reference(message: str, context: ConversationState) -> DisplayedProduct | None:
        """Resolve current, previous, ordinal, and pronoun product references."""

        text = message.lower()
        current = context.displayed_products
        previous = context.previous_displayed_products
        if "previous" in text:
            return context.selected_product or (previous[0] if previous else None)
        for word, position in ORDINALS.items():
            if word in text:
                return next((item for item in current if item.position == position), None)
        number = re.search(r"(?:number|option|product)\s*(\d+)", text)
        if number:
            position = int(number.group(1))
            return next((item for item in current if item.position == position), None)
        for item in current:
            if item.product_name.lower() in text:
                return item
        if any(word in text for word in ("it", "this", "that", "one")):
            return context.selected_product or (current[0] if len(current) == 1 else None)
        return context.selected_product if not current else None

    @staticmethod
    def _exact_option(details: ProductDetails, reference: DisplayedProduct) -> ProductOption | None:
        """Return the exact variant/branch option originally shown."""

        return next(
            (
                item for item in details.options
                if item.variant_id == reference.variant_id and item.branch_id == reference.branch_id
            ),
            details.options[0] if details.options else None,
        )

    @staticmethod
    def _details_reply(details: ProductDetails, reference: DisplayedProduct) -> str:
        """Build a concise factual product-details response."""

        details_bits = [value for value in (details.material, details.fit, details.season) if value]
        detail_text = ", ".join(details_bits)
        suffix = f" It’s {detail_text}." if detail_text else ""
        return f"{reference.product_name} is PKR {reference.price} in {reference.color}, size {reference.size}.{suffix}"
