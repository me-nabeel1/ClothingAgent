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
            sizes_val = payload.sizes
            if isinstance(sizes_val, dict):
                for k, v in sizes_val.items():
                    state.size_preferences[k] = v
            elif isinstance(sizes_val, list) and sizes_val:
                state.size_preferences["general"] = str(sizes_val[0])
            elif isinstance(sizes_val, str) and sizes_val.strip():
                state.size_preferences["general"] = sizes_val.strip()
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
        
        if not response.products:
            return "No products found matching the criteria."

        # Multi-category / subcategory 3-item cap per group
        grouped_products: dict[str, list[Any]] = {}
        for p in response.products:
            key = p.product_type or p.category or "Items"
            if key not in grouped_products:
                grouped_products[key] = []
            if len(grouped_products[key]) < 3:
                grouped_products[key].append(p)
                
        final_products = [p for group in grouped_products.values() for p in group]
        
        state.record_displayed_products(final_products)
        state.product_cards = [ProductCard(product=p) for p in final_products]

        lines = ["Here are the available options matching your request (up to 3 options per category/style):"]
        opt_idx = 1
        for cat_key, items in grouped_products.items():
            lines.append(f"\n--- {cat_key.title()} Options ---")
            for p in items:
                price_int = int(float(p.final_price)) if p.final_price is not None else 0
                colors_str = ", ".join(sorted(list(set(v.color for v in p.variants if v.is_available)))) if p.variants else "Various"
                sizes_str = ", ".join(sorted(list(set(v.size for v in p.variants if v.is_available)))) if p.variants else "Various"
                lines.append(f"Option {opt_idx}: {p.product_name} - {price_int} rupees (Colors: {colors_str} | Sizes: {sizes_str})")
                opt_idx += 1
                
        lines.append("\nINSTRUCTION: Present these options to the customer clearly grouped by category/style. Conclude by asking a warm follow-up: 'Please let me know your preference for color, size, or occasion so I can bring options tailored specifically to your style and preference, or add them to your bag!'")
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

        query_str = getattr(payload, "search_query", None) if payload else None
        if not query_str and hasattr(payload, "product_name") and getattr(payload, "product_name", None):
            query_str = getattr(payload, "product_name")
        if not query_str and hasattr(payload, "query") and getattr(payload, "query", None):
            query_str = getattr(payload, "query")

        if not query_str and state.message_history:
            last_msg = next((m.get("content", "") for m in reversed(state.message_history) if m.get("role") == "user"), "")
            if last_msg:
                cleaned_msg = re.sub(r"^(tell me more about|show details for|details of|details for|what about|tell about)\s+", "", last_msg, flags=re.IGNORECASE).strip()
                if cleaned_msg:
                    query_str = cleaned_msg

        if not target_product_ids and query_str:
            search_res = await self._client.search_products(ProductSearchRequest(query_text=query_str, in_stock_only=False, limit=5))
            if search_res and search_res.products:
                target_product_ids = [p.product_id for p in search_res.products[:2]]

        if not target_product_ids and state.displayed_products:
            target_product_ids = [dp.product_id for dp in state.displayed_products[:2]]

        if not target_product_ids:
            return None

        state.clear_cards()
        detailed_products = []
        lines = []

        req_color = None
        req_size = None

        if payload:
            colors_val = getattr(payload, "colors", None) or getattr(payload, "preferred_colors", None)
            if colors_val and isinstance(colors_val, list) and colors_val:
                req_color = colors_val[0]
            sizes_val = getattr(payload, "sizes", None) or getattr(payload, "size_preferences", None)
            if isinstance(sizes_val, dict) and sizes_val:
                req_size = list(sizes_val.values())[0]
            elif isinstance(sizes_val, list) and sizes_val:
                req_size = sizes_val[0]
            elif isinstance(sizes_val, str):
                req_size = sizes_val

        if not req_color and state.preferred_colors:
            req_color = state.preferred_colors[0]
        if not req_size and state.size_preferences:
            req_size = list(state.size_preferences.values())[0]

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
            state.selected_product_id = detailed_products[0].product_id
            return "\n\n".join(lines)
        return None

    async def get_products(self, state: ConversationState, payload: Optional[SearchProductsPayload] = None, limit_override: Optional[int] = None) -> Any:
        return await self.search(state, payload, limit_override)

    async def explore_category(self, state: ConversationState, payload: Any = None) -> Any:
        return await self.search(state, payload)

    async def get_product_details(self, arg1: Any, arg2: Any = None) -> Any:
        return await self.get_details(arg1, arg2)
