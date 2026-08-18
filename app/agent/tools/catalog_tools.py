"""Catalog tool handlers for product search, category exploration, and details retrieval."""

import logging
import re
from typing import Optional, Any

from app.agent.state import ConversationState, ProductCard
from app.agent.schemas import SearchProductsPayload, GetProductDetailsPayload, ExploreCategoryPayload
from app.agent.tools.helpers import parse_categories_from_input
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import ProductSearchRequest

logger = logging.getLogger(__name__)


class CatalogToolsMixin:
    """Catalog interaction capabilities."""

    _client: ClothingAppClient

    async def search(
        self,
        state: ConversationState,
        payload: Optional[SearchProductsPayload] = None,
        limit_override: Optional[int] = None
    ) -> str:
        state.clear_cards()
        if payload is None:
            payload = SearchProductsPayload()
        
        if getattr(payload, "clear_previous_preferences", False):
            state.clear_search_preferences()
            
        categories_val = getattr(payload, "categories", None)
        query_val = getattr(payload, "search_query", None)
        category_name_val = getattr(payload, "category_name", None)
        if category_name_val and not categories_val:
            categories_val = [category_name_val]

        if categories_val is not None:
            parsed = parse_categories_from_input(categories_val, query_val)
            if parsed:
                state.categories = parsed
        elif not state.categories and query_val:
            parsed = parse_categories_from_input(None, query_val)
            if parsed:
                state.categories = parsed

        if getattr(payload, "product_types", None) is not None: state.product_types = payload.product_types
        if getattr(payload, "occasions", None) is not None: state.occasions = payload.occasions
        if getattr(payload, "colors", None) is not None: state.preferred_colors = payload.colors
        if getattr(payload, "excluded_colors", None) is not None: state.excluded_colors = payload.excluded_colors
        if getattr(payload, "materials", None) is not None: state.materials = payload.materials
        if getattr(payload, "fits", None) is not None: state.fits = payload.fits
        if getattr(payload, "seasons", None) is not None: state.seasons = payload.seasons
        if getattr(payload, "branch", None) is not None: state.branch_preference = payload.branch
        if getattr(payload, "sizes", None) is not None:
            for k, v in payload.sizes.items():
                state.size_preferences[k] = v
        if getattr(payload, "budget", None) is not None:
            if payload.budget.minimum is not None: state.budget.minimum = payload.budget.minimum
            if payload.budget.maximum is not None: state.budget.maximum = payload.budget.maximum
            
        budget_min = state.budget.minimum
        budget_max = state.budget.maximum
        
        if budget_max is None and state.displayed_products:
            min_displayed_price = min((p.price for p in state.displayed_products if p.price > 0), default=None)
            if min_displayed_price is not None:
                budget_max = float(min_displayed_price) - 0.01

        if limit_override is not None:
            limit = limit_override
        else:
            cats = state.categories or []
            limit = max(6, 3 * len(cats))
            limit = min(limit, 20)

        request = ProductSearchRequest(
            query_text=getattr(payload, "search_query", None),
            categories=state.categories,
            product_types=state.product_types,
            occasions=state.occasions,
            colors=state.preferred_colors,
            excluded_colors=state.excluded_colors,
            size_mapping=state.size_preferences,
            excluded_product_ids=list(state.seen_product_ids),
            materials=state.materials,
            fits=state.fits,
            seasons=state.seasons,
            minimum_price=budget_min,
            maximum_price=budget_max,
            branch_code=None,  # Always pool stock across all branches for online shopping
            in_stock_only=True,
            limit=min(limit, 20),
            article_code=getattr(payload, "specific_article", None),
        )

        logger.info(
            "agent_tool_get_products",
            extra={"event": "agent_tool_get_products", "filters": request.model_dump(exclude_defaults=True)},
        )

        response = await self._client.search_products(request)
        
        if state.categories and response.products:
            def _is_tshirt_field(text: str) -> bool:
                return bool(re.search(r'\b(t-shirt|t-shirts|tshirt|tshirts|tee|tees)\b', text, re.IGNORECASE))

            def _matches_category(p, requested_cats):
                fields = [(p.category or "").lower(), (p.product_name or "").lower(), (p.product_type or "").lower()]
                has_tshirt = any(_is_tshirt_field(f) for f in fields)
                combined_clean = " ".join(fields)

                for req in requested_cats:
                    req_clean = req.lower().replace(" ", "").replace("-", "").rstrip("s")

                    if req_clean in ("tshirt", "tee"):
                        if has_tshirt:
                            return True
                        return False

                    if req_clean == "shirt":
                        if has_tshirt:
                            return False
                        if "shirt" in combined_clean:
                            return True
                        return False

                    if req_clean in ("jean", "denim"):
                        if "jean" in combined_clean or "denim" in combined_clean:
                            return True
                        return False

                    if req_clean == "pant":
                        if any(re.search(r'\b(pants?)\b', f, re.IGNORECASE) for f in fields):
                            return True
                        return False

                    if req_clean == "trouser":
                        if any(re.search(r'\b(trousers?)\b', f, re.IGNORECASE) for f in fields):
                            return True
                        return False

                    if req_clean in combined_clean.replace(" ", "").replace("-", ""):
                        return True
                return False

            matched = [p for p in response.products if _matches_category(p, state.categories)]
            response.products = matched[:limit]
            response.result_count = len(response.products)
        else:
            response.products = response.products[:limit]
            response.result_count = len(response.products)

        query_text = (query_val or "").lower()
        is_general_query = any(phrase in query_text for phrase in [
            "what products", "what categories", "what do you sell", "what items", "what collection",
            "show products", "show categories", "tell me about", "what styles", "what outfits"
        ])
        
        if is_general_query and not categories_val and not state.categories and not state.preferred_colors and not state.size_preferences:
            state.displayed_products.clear()
            state.product_cards.clear()
        else:
            state.record_displayed_products(response.products)
            state.product_cards = [ProductCard(product=p) for p in response.products]
        
        if not response.products:
            return "No products found matching the criteria."
        lines = [f"Found {len(response.products)} products:"]
        for idx, p in enumerate(response.products, 1):
            price_int = int(float(p.final_price)) if p.final_price is not None else 0
            lines.append(f"Option {idx}: {p.product_name} - {price_int} rupees.")
        return "\n".join(lines)

    async def get_details(self, arg1: Any, arg2: Any = None) -> Any:
        if isinstance(arg1, ConversationState):
            state, payload = arg1, arg2
        else:
            payload, state = arg1, arg2

        if not state:
            return None

        product_id = getattr(payload, "product_id", None) if payload else None
        selected_index = getattr(payload, "selected_product_index", None) if payload else None

        target_product_ids = []
        if product_id:
            target_product_ids.append(product_id)
        elif selected_index is not None and state.displayed_products:
            if 1 <= selected_index <= len(state.displayed_products):
                target_product_ids.append(state.displayed_products[selected_index - 1].product_id)

        if not target_product_ids and state.displayed_products:
            target_product_ids = [dp.product_id for dp in state.displayed_products]

        if not target_product_ids:
            return None

        state.clear_cards()
        detailed_products = []
        lines = []

        req_color = state.preferred_colors[0] if state.preferred_colors else None
        req_size = list(state.size_preferences.values())[0] if state.size_preferences else None

        for pid in target_product_ids:
            logger.info(
                "agent_tool_get_product_details",
                extra={"event": "agent_tool_get_product_details", "product_id": pid},
            )
            details = await self._client.get_product(pid)
            if details and details.product:
                p = details.product
                detailed_products.append(p)
                price_int = int(float(p.final_price)) if p.final_price is not None else 0
                line_entry = [f"Details for {p.product_name}:", f"Price: {price_int} rupees.", f"Description: {p.description or 'N/A'}."]
                
                if p.variants:
                    all_avail = [v for v in p.variants if v.is_available]
                    all_colors = sorted(list(set(v.color for v in all_avail)))
                    all_sizes = sorted(list(set(v.size for v in all_avail)))

                    exact_matches = [
                        v for v in all_avail
                        if (not req_color or v.color.lower() == req_color.lower())
                        and (not req_size or str(v.size).lower() == str(req_size).lower())
                    ]

                    if exact_matches:
                        line_entry.append("Status: Available for online ordering.")
                        if req_color and req_size:
                            line_entry.append(f"Requested Variant ({req_color} size {req_size}): IN STOCK for nationwide delivery.")
                        line_entry.append(f"Available Colors: {', '.join(all_colors) if all_colors else 'None'}")
                        line_entry.append(f"Available Sizes: {', '.join(all_sizes) if all_sizes else 'None'}")
                    else:
                        same_size_avail = [
                            v for v in all_avail
                            if req_size and str(v.size).lower() == str(req_size).lower()
                        ]
                        same_size_colors = sorted(list(set(v.color for v in same_size_avail)))

                        same_color_avail = [
                            v for v in all_avail
                            if req_color and v.color.lower() == req_color.lower()
                        ]
                        same_color_sizes = sorted(list(set(v.size for v in same_color_avail)))

                        if req_color and req_size and same_size_colors:
                            line_entry.append(
                                f"Smart Variant Recommendation: The {req_color} color is currently out of stock in size {req_size}. "
                                f"However, we do have size {req_size} available in {', '.join(same_size_colors)}. "
                                f"Would you like to select one of these available colors?"
                            )
                        elif req_color and req_size and same_color_sizes:
                            line_entry.append(
                                f"Smart Variant Recommendation: Size {req_size} is currently out of stock in {req_color}. "
                                f"However, we do have {req_color} available in sizes {', '.join(same_color_sizes)}. "
                                f"Would you like to select one of these available sizes?"
                            )
                        else:
                            line_entry.append(f"Available Colors: {', '.join(all_colors) if all_colors else 'None'}")
                            line_entry.append(f"Available Sizes: {', '.join(all_sizes) if all_sizes else 'None'}")

                lines.append("\n".join(line_entry))

        if detailed_products:
            state.record_displayed_products(detailed_products)
            state.product_cards = [ProductCard(product=p) for p in detailed_products]
            return "\n\n".join(lines)
        return None

    async def get_products(self, state: ConversationState, payload: Optional[SearchProductsPayload] = None, limit_override: Optional[int] = None) -> Any:
        return await self.search(state, payload, limit_override)

    async def explore_category(self, state: ConversationState, payload: Any = None) -> Any:
        return await self.search(state, payload)

    async def get_product_details(self, arg1: Any, arg2: Any = None) -> Any:
        return await self.get_details(arg1, arg2)
