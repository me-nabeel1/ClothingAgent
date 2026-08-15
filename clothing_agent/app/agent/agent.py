"""The core single-agent engine using Tool Calling."""

import logging
import json
from typing import Optional

from app.agent.state import ConversationState
from app.agent.tools import AgentTools
from app.agent.schemas import (
    tools as AGENT_TOOLS,
    ExploreCategoryPayload,
    SearchProductsPayload,
    GetProductDetailsPayload,
    AddCartItemPayload,
    RemoveCartItemPayload,
    ShowCartPayload,
    PreviewCheckoutPayload,
    PlaceOrderPayload,
    GetPromotionsPayload
)
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage
from app.llm.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class SingleAgent:
    """The authoritative AI agent orchestrating conversation and business logic."""

    def __init__(self, llm: LLMClient, tools: AgentTools) -> None:
        self._llm = llm
        self._tools = tools

    async def process_message(
        self,
        user_message: str,
        state: ConversationState,
        context: StoreContext,
    ) -> str:
        """Process one conversational turn using Tool Calling."""
        logger.info("agent_processing_message", extra={"event": "process_message"})

        # Reset turn intent for the new turn
        state.current_intent = "general"

        # Detect general store inquiry and clear past search preferences & displayed products
        msg_lower = user_message.lower().strip()
        general_keywords = (
            "what products", "what product", "what do you offer", "what do you sell",
            "what categories", "show categories", "what items do you have", "what can i buy",
            "tell me what you have", "list products", "list categories", "what you have"
        )
        is_general_store_query = any(q in msg_lower for q in general_keywords) and not any(
            c in msg_lower for c in ("shirt", "pant", "trouser", "hoodie", "jacket", "kurta", "jean")
        )
        if is_general_store_query:
            state.clear_search_preferences()
            state.displayed_products.clear()

        # 1. Append user message to history
        state.message_history.append({"role": "user", "content": user_message})

        # 2. Build system context
        system_content = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Current State:\n{state.model_dump_json(exclude_defaults=True)}\n\n"
            "Available Vocabulary (Must match EXACTLY if used for filters):\n"
            f"Categories: {context.categories}\n"
            f"Product Types: {context.product_types}\n"
            f"Occasions: {context.occasions}\n"
            f"Colors: {context.colors}\n"
            f"Sizes: {context.sizes}\n"
            f"Materials: {context.supported_attributes}\n"
            f"Seasons: {context.seasons if hasattr(context, 'seasons') else []}\n"
            f"Branches: {[b.branch_code for b in context.branches]}\n\n"
            "- CUSTOMER INTENT GUIDANCE:\n"
            "  1. BROAD STORE OFFERINGS INTENT (e.g. 'What products/categories do you offer?', 'What do you sell?', 'What products you have?'): Do NOT search for specific items. Inform the customer of our main categories (Shirts, T-Shirts, Pants, Trousers, Outerwear, Traditional) and ask which category they would like to explore. DO NOT reference or summarize previously discussed products or past search results from earlier in the conversation.\n"
            "  2. CATEGORY EXPLORATION INTENT (e.g. 't shirts', 'what shirts do you have?', 'show me pants'): ALWAYS invoke `explore_category(category_name=...)`. Present 2-3 featured products in that category AND inform the customer of available subcategories/styles within that category.\n"
            "  3. IN-CATEGORY EXPANSION INTENT (e.g. 'What other products do you have in it?', 'Show more shirts'): Invoke `search_products` for the current category to retrieve and present additional items in that category.\n"
            "- STRICT CATEGORY RELEVANCE: ONLY list and present products that strictly belong to the user's requested item category (e.g. if user asks for a shirt, ONLY present shirts/polos/t-shirts; NEVER present pants, hoodies, or other unrelated categories).\n"
            "- When presenting products to the user, ALWAYS dynamically and professionally open the message appropriate to the query, then list the products exactly in this numbered format:\n"
            "  1. [Product Name] colors([colors]) and available sizes([sizes]) [price]\n"
            "  2. ...\n"
            "  Conclude the message by asking a relevant follow-up question (e.g. asking which they'd like to see details for or add to cart).\n"
            "- STRICT PRESENTATION RULE: You MUST ONLY discuss, list, and mention the specific products that were just returned by your MOST RECENT `search_products` or `explore_category` tool call. NEVER list or combine products from earlier in the conversation history, as they are no longer visible on the user's screen. The products you list in text MUST perfectly match the tool output.\n"
            "- ALWAYS SHOW CART PRODUCTS: When show_cart is called or when user asks to show/view cart, you MUST ALWAYS explicitly list all products currently in the cart in your text response (name, color, size, quantity, unit price, and subtotal).\n"
            "- NO PARENTHETICAL GUIDES OR EXAMPLE FORMATS: NEVER append parenthetical text like '(Please respond with the color and size you prefer, e.g. \"Beige, 32\")' or '(e.g. Navy, 34)' at the end of your response. Ask questions naturally in plain text without adding parenthetical formatting instructions.\n"
            "- CRITICAL INTENT & TOOL INVOCATION RULES:\n"
            "  * When user provides VARIANT SELECTION (e.g. 'navy 34', 'navy, 34', 'Beige 32', 'Navy', '34') following a prompt for color/size: You MUST IMMEDIATELY invoke the `add_cart_item` tool with the extracted color and size for the product in state. Do NOT output a text message promising to add it without calling `add_cart_item`. Do NOT ask for another confirmation.\n"
            "  * When user requests to ADD AN ITEM TO CART (e.g. 'add 1st in cart', 'add trouser in cart'): If color and size are provided, invoke `add_cart_item`. If color or size is missing, invoke `get_product_details` for that item to retrieve available colors and sizes, then ask the customer for their preferred color and size without appending parenthetical guides.\n"
            "  * When user requests to REMOVE AN ITEM FROM CART: invoke `remove_cart_item` (or `show_cart` if item index is ambiguous).\n"
            "  * When user requests to VIEW CART: invoke `show_cart`.\n"
            "  * When user requests CHECKOUT: invoke `preview_checkout`.\n"
            "  * When user confirms PLACE ORDER: invoke `place_order`.\n"
            "- Maintain a warm, professional, polite, and cooperative sales tone at all times.\n"
            "- After order placement, proactively cross-sell by offering exclusive deals, new arrivals, or trending items.\n"
        )
        
        # 3. Construct messages payload
        messages = [LLMMessage(role="system", content=system_content)]
        for msg in state.message_history:
            messages.append(LLMMessage(**msg))
            
        # 4. Multi-turn Agent Tool Execution Loop (up to 5 turns)
        max_turns = 5
        last_content = ""
        while max_turns > 0:
            max_turns -= 1
            logger.info("generating_agent_response_with_tools", extra={"turns_left": max_turns})
            content, tool_calls = await self._llm.generate_with_tools(messages, tools=AGENT_TOOLS)
            if content:
                last_content = content
                
            if not tool_calls:
                if content:
                    state.message_history.append({"role": "assistant", "content": content})
                    return content
                return last_content or "I have processed your request."
                
            # Append assistant tool call message to history & payload
            assistant_msg = {"role": "assistant", "content": content, "tool_calls": tool_calls}
            state.message_history.append(assistant_msg)
            messages.append(LLMMessage(**assistant_msg))
            
            has_search = any(tc.get("function", {}).get("name") in ["search_products", "explore_category"] for tc in tool_calls)
            if has_search:
                state.displayed_products.clear()
            
            # Execute all tool calls in this turn
            for tc in tool_calls:
                tc_id = tc.get("id")
                func_name = tc.get("function", {}).get("name")
                args_str = tc.get("function", {}).get("arguments", "{}")
                try:
                    args = json.loads(args_str)
                except Exception:
                    args = {}
                    
                from app.agent.checker import ParameterRequirementsChecker
                validation_error = await ParameterRequirementsChecker.check_action_requirements(func_name, args, state, self._tools)
                if validation_error:
                    result_str = validation_error
                else:
                    result_str = await self._execute_tool(func_name, args, state, context)
                
                tool_msg = {"role": "tool", "tool_call_id": tc_id, "content": result_str}
                state.message_history.append(tool_msg)
                messages.append(LLMMessage(**tool_msg))

        if last_content:
            state.message_history.append({"role": "assistant", "content": last_content})
            return last_content
        return "I have executed the requested actions."

    async def _execute_tool(self, func_name: str, args: dict, state: ConversationState, context: StoreContext) -> str:
        """Dispatch tool calls to AgentTools and return stringified results."""
        try:
            if func_name == "explore_category":
                state.current_intent = "search"
                payload = ExploreCategoryPayload(**args)
                res = await self._tools.explore_category(state, payload)
                
                cat_name = state.categories[0] if state.categories else payload.category_name
                if res.products:
                    subcats = sorted(list(set(p.product_type for p in res.products if p.product_type and p.product_type.lower() != cat_name.lower())))
                    subcats_info = f"Available subcategories/styles in {cat_name}: {', '.join(subcats)}." if subcats else ""
                    
                    lines = [f"Retrieved 2-3 featured products for category '{cat_name}':"]
                    for i, p in enumerate(res.products[:3], 1):
                        is_avail = any(v.is_available for v in p.variants) if hasattr(p, "variants") else True
                        avail_str = "Available" if is_avail else "Out of Stock"
                        lines.append(f"Option {i}: {p.product_name} | Price: Rs {p.final_price} | {avail_str}")
                        if hasattr(p, "variants"):
                            colors = sorted(list(set(v.color for v in p.variants if v.is_available)))
                            sizes = sorted(list(set(v.size for v in p.variants if v.is_available)))
                            lines.append(f"  Available Colors: {', '.join(colors) if colors else 'None'}")
                            lines.append(f"  Available Sizes: {', '.join(sizes) if sizes else 'None'}")
                    
                    if subcats_info:
                        lines.append(subcats_info)
                    lines.append(f"INSTRUCTION: Present these 2-3 featured {cat_name} options to the user, and inform them of available subcategories/styles in {cat_name} ({', '.join(subcats) if subcats else 'various styles'}). Ask if they would like to explore a subcategory, select an option for details, or add to cart. DO NOT append parenthetical response guides.")
                    return "\n".join(lines)
                
                avail_cats = ", ".join(context.categories) if hasattr(context, "categories") and context.categories else "Shirts, T-Shirts, Pants, Trousers, Outerwear, Traditional"
                return f"No products found in category '{cat_name}'. Available store categories: {avail_cats}. INSTRUCTION: Tell the user no products were found in '{cat_name}', list the available store categories ({avail_cats}), and ask which one they would like to explore."

            elif func_name == "search_products":
                state.current_intent = "search"
                payload = SearchProductsPayload(**args)
                res = await self._tools.get_products(state, payload)
                
                if res.products:
                    cats_str = " and ".join(state.categories) if state.categories else "the catalog"
                    lines = [f"Retrieved {len(res.products)} products for {cats_str}:"]
                    for i, p in enumerate(res.products, 1):
                        is_avail = any(v.is_available for v in p.variants) if hasattr(p, "variants") else True
                        avail_str = "Available" if is_avail else "Out of Stock"
                        cat_label = f" (Category: {p.category_name})" if hasattr(p, "category_name") and p.category_name else ""
                        lines.append(f"Option {i}: {p.product_name}{cat_label} | Price: Rs {p.final_price} | {avail_str}")
                        if hasattr(p, "variants"):
                            colors = sorted(list(set(v.color for v in p.variants if v.is_available)))
                            sizes = sorted(list(set(v.size for v in p.variants if v.is_available)))
                            lines.append(f"  Available Colors: {', '.join(colors) if colors else 'None'}")
                            lines.append(f"  Available Sizes: {', '.join(sizes) if sizes else 'None'}")
                    lines.append(f"INSTRUCTION: Present products clearly for ALL requested categories ({cats_str}) to the user. Show options for each requested category. DO NOT append parenthetical response guides.")
                    return "\n".join(lines)
                
                avail_cats = ", ".join(context.categories) if hasattr(context, "categories") and context.categories else "Shirts, T-Shirts, Pants, Trousers, Outerwear, Traditional"
                return f"No products found matching these specific criteria. Available store categories are: {avail_cats}. INSTRUCTION: Tell the user no items matched their query, inform them of our available categories ({avail_cats}), and ask which category they would like to explore."
                
            elif func_name == "get_product_details":
                state.current_intent = "get_details"
                payload = GetProductDetailsPayload(**args)
                details = await self._tools.get_product_details(payload, state)
                if details:
                    p = details.product
                    # Summarize variants
                    available_colors = set()
                    available_sizes = set()
                    for v in p.variants:
                        if v.is_available:
                            available_colors.add(v.color)
                            available_sizes.add(v.size)
                    
                    return (
                        f"Product Details for {p.product_name} (ID: {p.product_id})\n"
                        f"Price: {p.final_price}\n"
                        f"Available Colors: {', '.join(available_colors) if available_colors else 'None'}\n"
                        f"Available Sizes: {', '.join(available_sizes) if available_sizes else 'None'}"
                    )
                return "Product not found or not selected."
                
            elif func_name == "add_cart_item":
                payload = AddCartItemPayload(**args)
                cart = await self._tools.add_cart_item(state, payload)
                if cart:
                    state.displayed_products.clear()
                    color_size_str = f" ({payload.color}, Size {payload.size})" if payload.color and payload.size else ""
                    return f"Item{color_size_str} successfully added to cart. INSTRUCTION: Confirm to the user that the item{color_size_str} has been added to their cart, and ask if they wish to proceed to checkout or explore more products. DO NOT append parenthetical response guides or example text."

                # Fetch product details to report available variants to LLM for clarification or out-of-stock reporting
                product_id = payload.product_id or state.selected_product_id
                if not product_id and payload.selected_product_index is not None:
                    idx = payload.selected_product_index
                    if 1 <= idx <= len(state.displayed_products):
                        product_id = state.displayed_products[idx - 1].product_id
                if not product_id and state.displayed_products:
                    product_id = state.displayed_products[0].product_id

                if product_id:
                    details = await self._tools.get_product_details(GetProductDetailsPayload(product_id=product_id), state)
                    if details and details.product and details.product.variants:
                        p = details.product
                        colors = sorted(list(set(v.color for v in p.variants if v.is_available)))
                        sizes = sorted(list(set(v.size for v in p.variants if v.is_available)))
                        
                        if payload.color and payload.size:
                            return (
                                f"The requested variant (Color: '{payload.color}', Size: '{payload.size}') is currently out of stock or unavailable for {p.product_name}.\n"
                                f"Available Colors in stock: {', '.join(colors) if colors else 'None'}\n"
                                f"Available Sizes in stock: {', '.join(sizes) if sizes else 'None'}\n"
                                "INSTRUCTION: Politely inform the user that their requested color/size variant is currently unavailable in stock, list the available colors and sizes, and ask them to choose from the available options. DO NOT append parenthetical response guides."
                            )
                        
                        return (
                            f"Cannot add {p.product_name} to cart directly because variant selection (color and size) is required.\n"
                            f"Available Colors: {', '.join(colors) if colors else 'None'}\n"
                            f"Available Sizes: {', '.join(sizes) if sizes else 'None'}\n"
                            "INSTRUCTION: Politely and professionally ask the user which color and size they prefer from the available options before adding to cart. DO NOT append parenthetical response guides or example text (e.g. do not add '(Please respond with...)')."
                        )
                return "Failed to add item. Ensure size and color are specified and the item is in stock. INSTRUCTION: Professionally ask the user to clarify their preferred size and color. DO NOT append parenthetical guides."
                
            elif func_name == "remove_cart_item":
                payload = RemoveCartItemPayload(**args)
                cart = await self._tools.remove_cart_item(state, payload)
                if cart:
                    return "Item successfully removed from cart."
                return "Failed to remove item. The cart might be empty or the item was not found."
                
            elif func_name == "show_cart":
                if state.cart.items:
                    lines = [f"Cart Subtotal: Rs {state.cart.subtotal:.2f}"]
                    for i, item in enumerate(state.cart.items, 1):
                        lines.append(f"{i}. {item.product_name} - Color: {item.color}, Size: {item.size} (Qty: {item.quantity}) - Rs {item.price:.2f}")
                    cart_str = "\n".join(lines)
                    return f"Current Cart Items:\n{cart_str}\nINSTRUCTION: You MUST explicitly list ALL these cart items in your text response to the user with their name, color, size, quantity, and price. Conclude by asking if they want to proceed to checkout or keep shopping."
                return "The cart is currently empty. INSTRUCTION: Inform the user that their cart is currently empty and ask if they would like to explore products."
                
            elif func_name == "preview_checkout":
                state.current_intent = "checkout"
                state.displayed_products.clear()
                preview = await self._tools.preview_checkout(state)
                if preview:
                    return f"Checkout Preview Ready. Total: {preview.total_amount}. INSTRUCTION: Do NOT list the specific products in the cart. Ask the user for their delivery details (name, phone, address, city) to proceed with placing the order."
                return "Cart is empty."
                
            elif func_name == "place_order":
                payload = PlaceOrderPayload(**args)
                state.displayed_products.clear()
                order = await self._tools.place_order(state, payload)
                if order:
                    return f"Order placed successfully! Order Number: {order.order_number}. INSTRUCTION: Say the order is confirmed, will dispatch shortly (5-7 days). Then proactively cross-sell by offering exclusive deals or trending items. DO NOT end the conversation awkwardly."
                return "Failed to place order. Cart might be empty or details invalid."
                
            elif func_name == "get_promotions":
                return await self._tools.get_promotions()
                
            else:
                return f"Unknown tool: {func_name}"
                
        except Exception as e:
            logger.error(f"Error executing tool {func_name}: {e}")
            return f"Error executing tool {func_name}: {str(e)}"
