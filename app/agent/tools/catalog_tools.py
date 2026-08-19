"""Catalog tool handlers for product search, category exploration, and details retrieval."""

import logging
import re
from typing import Optional, Any

from app.agent.state import ConversationState, ProductCard
from app.agent.schemas import SearchProductsPayload, GetProductDetailsPayload, ExploreCategoryPayload
from app.agent.tools.helpers import parse_categories_from_input
from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import ProductSearchRequest

from app.agent.utils import detect_input_language

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

        sq = getattr(payload, "search_query", None)
        if state.categories and sq:
            sq = None

        # Flush seen_product_ids on new search queries to prevent old state filtering anomalies
        if payload and (getattr(payload, "categories", None) or sq):
            state.seen_product_ids.clear()

        request = ProductSearchRequest(
            query_text=sq,
            categories=state.categories,
            product_types=state.product_types,
            occasions=state.occasions,
            colors=state.preferred_colors,
            excluded_colors=state.excluded_colors,
            size_mapping=state.size_preferences,
            excluded_product_ids=[],
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

        # Broad category clarification map
        broad_category_keywords = {
            "shirt": ["T-Shirts", "Casual Cotton Shirts", "Formal Dress Shirts", "Polo Shirts"],
            "shirts": ["T-Shirts", "Casual Cotton Shirts", "Formal Dress Shirts", "Polo Shirts"],
            "pant": ["Jeans", "Trousers", "Track Pants", "Shorts"],
            "pants": ["Jeans", "Trousers", "Track Pants", "Shorts"],
            "clothes": ["T-Shirts", "Casual Shirts", "Dress Shirts", "Pants", "Activewear", "Jackets"],
            "clothing": ["T-Shirts", "Casual Shirts", "Dress Shirts", "Pants", "Activewear", "Jackets"],
            "wear": ["T-Shirts", "Casual Shirts", "Dress Shirts", "Pants", "Activewear", "Jackets"],
            "suit": ["Formal Suits", "Tracksuits", "Dress Shirts"],
            "activewear": ["Track Pants", "Running Shorts", "Joggers", "Tracksuits"],
            "outerwear": ["Fleece Jackets", "Hoodies", "Denim Jackets", "Sweatshirts"],
            "jacket": ["Fleece Jackets", "Hoodies", "Denim Jackets", "Sweatshirts"],
            "jackets": ["Fleece Jackets", "Hoodies", "Denim Jackets", "Sweatshirts"],
        }
        
        specific_subcategories = {
            "t-shirts", "t-shirt", "tshirt", "tshirts", "polo shirts", "polo shirt",
            "casual cotton shirts", "formal dress shirts", "jeans", "trousers",
            "running shorts", "track pants", "joggers", "fleece jackets", "hoodies", "denim jackets"
        }
        
        has_specific_category = any(
            c.lower().strip() in specific_subcategories for c in (state.categories or [])
        )

        has_specific_filter = bool(
            getattr(payload, "colors", None) or
            getattr(payload, "sizes", None) or
            getattr(payload, "specific_article", None) or
            state.preferred_colors or
            state.size_preferences or
            has_specific_category
        )
        
        matched_broad_key = None
        for key in broad_category_keywords:
            if re.search(rf"\b{key}\b", query_text):
                matched_broad_key = key
                break
        if not matched_broad_key and state.categories and len(state.categories) == 1:
            cat_name = state.categories[0].lower()
            for key in broad_category_keywords:
                if key in cat_name:
                    matched_broad_key = key
                    break

        vague_phrases = [
            "buy shirts", "want shirts", "need shirts", "show shirts", "buy clothes", "want clothes",
            "buy pants", "want pants", "show pants", "buy activewear", "want activewear", "show clothes",
            "i want shirts", "i want to buy shirts", "i want pants", "i want clothes", "i want clothing"
        ]
        
        is_vague_query = any(p in query_text for p in vague_phrases) or query_text in ("shirts", "shirt", "pants", "pant", "clothes", "clothing", "wear")

        if is_vague_query and not has_specific_filter and getattr(payload, "selected_product_index", None) is None:
            subcats = "T-Shirts, Casual Cotton Shirts, Formal Dress Shirts, Polo Shirts, Jeans, Trousers, Track Pants, Shorts"
            if "pant" in query_text:
                subcats = "Jeans, Trousers, Track Pants, Shorts"
            elif "shirt" in query_text:
                subcats = "T-Shirts, Casual Cotton Shirts, Formal Dress Shirts, Polo Shirts"
            elif "active" in query_text:
                subcats = "Track Pants, Running Shorts, Joggers, Tracksuits"
                
            state.displayed_products.clear()
            state.product_cards.clear()
            return (
                f"VAGUE CATEGORY INQUIRY DETECTED:\n"
                f"Available subcategories/styles: {subcats}.\n"
                "INSTRUCTION: Do NOT assume or hallucinate the customer's intent and DO NOT output product cards.\n"
                "Reply professionally listing these available subcategories/styles and ask a clarifying question:\n"
                f"English Example: 'In our collection, we have {subcats} available. If you tell me what specific style, color, size, or occasion you prefer, I can bring the best match for you!'\n"
                "Urdu Script Example: 'ہماری کلیکشن میں یہ تمام اسٹائلز موجود ہیں۔ اگر آپ مجھے اپنا پسندیدہ اسٹائل، رنگ، سائز یا موقع بتائیں تو میں آپ کے لیے بہترین انتخاب لاتا ہوں!'"
            )

        is_category_list_query = any(phrase in query_text for phrase in [
            "categories", "category", "کیٹیگری", "کیٹیگریز", "what categories", "product categories"
        ])
        
        if is_category_list_query:
            state.displayed_products.clear()
            state.product_cards.clear()
            return (
                "DYNAMIC CATEGORY LISTING RESPONSE:\n"
                "In our menswear collection, we have the following product categories available:\n"
                "1 T-Shirts & Polo Tees\n"
                "2 Shirts (Casual & Formal)\n"
                "3 Pants, Jeans & Trousers\n"
                "4 Activewear & Shorts\n"
                "5 Jackets & Outerwear\n\n"
                "INSTRUCTION: Dynamically list these available menswear categories in the customer's language (English or Urdu script) as a clean numbered list (1, 2, 3, 4, 5 with NO period directly after the digit 1, 2, 3). Ask the customer which category or style they would like to explore today. DO NOT repeat general discount text and DO NOT output product cards."
            )

        is_general_query = any(phrase in query_text for phrase in [
            "what products", "what do you sell", "what items", "what collection",
            "show products", "tell me about", "what styles", "what outfits",
            "store offerings", "what do you have", "what you have", "discounts", "offers",
            "what we have"
        ])

        if is_general_query or query_text in ("store offerings", "what do you have", "what you have", "what we have"):
            state.displayed_products.clear()
            state.product_cards.clear()
            return (
                "GENERAL STORE INQUIRY RESPONSE:\n"
                "We offer a wide range of premium menswear apparel across our collections (T-Shirts, Shirts, Pants, Activewear, Jackets, Outerwear) with handsome discounts right now!\n"
                "If you want, I can tell you how you can get your favorite product and can help you to get maximum discounts we are offering right now.\n"
                "INSTRUCTION: Politely reply explaining our premium menswear products and active handsome discounts. Explicitly keep focus ONLY on Men's clothing (never mention Women, Kids, or Unisex). Offer to help the customer find their favorite product and get maximum discounts, and ask which category or style they would like to explore today. DO NOT output any product cards."
            )

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

        # Detect user language
        last_user_msg = ""
        for msg in reversed(state.message_history):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        user_lang = detect_input_language(last_user_msg)

        from app.agent.formatters import format_product_listing_schema
        return format_product_listing_schema(grouped_products, user_lang=user_lang)

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
                line_entry = [
                    f"Product Details:",
                    f"- Name: {p.product_name}.",
                    f"- Price: {price_int} rupees.",
                    f"- Description: {p.description or 'N/A'}.",
                ]
                
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
                        line_entry.append("- Status: Available for online ordering.")
                        if req_color and req_size:
                            line_entry.append(f"- Requested Variant ({req_color}, Size {req_size}): IN STOCK.")
                        line_entry.append(f"- Available Colors: {', '.join(all_colors) if all_colors else 'None'}.")
                        line_entry.append(f"- Available Sizes: {', '.join(all_sizes) if all_sizes else 'None'}.")
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

            # Detect user language
            last_user_msg = ""
            for msg in reversed(state.message_history):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "")
                    break
            user_lang = detect_input_language(last_user_msg)

            from app.agent.formatters import format_product_details_schema
            return format_product_details_schema(detailed_products[0], user_lang=user_lang)
        return None

    async def get_products(self, state: ConversationState, payload: Optional[SearchProductsPayload] = None, limit_override: Optional[int] = None) -> Any:
        return await self.search(state, payload, limit_override)

    async def explore_category(self, state: ConversationState, payload: Any = None) -> Any:
        return await self.search(state, payload)

    async def get_product_details(self, arg1: Any, arg2: Any = None) -> Any:
        return await self.get_details(arg1, arg2)
