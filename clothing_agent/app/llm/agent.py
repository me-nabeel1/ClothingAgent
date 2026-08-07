import json
import logging
from typing import Any
from uuid import UUID
import pathlib

from app.clients.clothing_app.client import ClothingAppClient
from app.clients.clothing_app.schemas import ProductSearchRequest, AddCartItemRequest
from app.core.config import AgentConfig
from app.core.conversation import ConversationState
from app.llm.client import LLMClient, LLMMessage

logger = logging.getLogger(__name__)

class MonolithicAgentService:
    def __init__(self, llm: LLMClient, clothing_app: ClothingAppClient, config: AgentConfig):
        self._llm = llm
        self._clothing_app = clothing_app
        self._config = config
        
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "prompt.txt"
        with open(prompt_path, encoding="utf-8") as f:
            self._prompt = f.read()
            
    def _get_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search for products based on constraints.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query_text": {"type": "string"},
                            "category": {"type": "string"},
                            "color": {"type": "string", "description": "A single color, e.g. 'Red'"},
                            "size": {"type": "string", "description": "A single size, e.g. 'Large'"},
                            "minimum_price": {"type": "string"},
                            "maximum_price": {"type": "string"},
                            "semantic_tags": {"type": "string", "description": "Comma-separated tags"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_cart",
                    "description": "Add a specific product variant to the cart. If you only know the product_id, you must first search for the product to get its variant_id and branch_id.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "variant_id": {"type": "integer"},
                            "branch_id": {"type": "integer"},
                            "quantity": {"type": "integer"}
                        },
                        "required": ["variant_id", "branch_id", "quantity"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "view_cart",
                    "description": "View the current contents of the user's shopping cart.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remove_from_cart",
                    "description": "Remove an item from the cart by item_id.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "item_id": {"type": "string"}
                        },
                        "required": ["item_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "clear_cart",
                    "description": "Clear all items from the cart.",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
        
    async def _execute_tool(self, tool_call: dict[str, Any], state: ConversationState) -> tuple[str, list, Any]:
        """Execute tool and return (json_string_result, products, cart)"""
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"].get("arguments", "{}"))
        products = []
        cart = None
        
        try:
            if name == "search_products":
                # Map flat string params to lists for the actual API request
                if "color" in args:
                    args["colors"] = [args.pop("color")]
                if "size" in args:
                    args["sizes"] = [args.pop("size")]
                if "semantic_tags" in args:
                    tags_str = args.pop("semantic_tags")
                    if isinstance(tags_str, str):
                        args["semantic_tags"] = [t.strip() for t in tags_str.split(",") if t.strip()]
                        
                req = ProductSearchRequest(**args)
                req.limit = self._config.displayed_product_limit
                res = await self._clothing_app.search_products(req)
                products = res.products
                return json.dumps({"status": "success", "found_count": len(products), "products": [p.model_dump(mode="json") for p in products]}), products, None
                
            elif name == "add_to_cart":
                if not state.cart_id:
                    c = await self._clothing_app.create_cart()
                    state.cart_id = c.cart_id
                req = AddCartItemRequest(**args)
                cart = await self._clothing_app.add_cart_item(state.cart_id, req)
                return json.dumps({"status": "success", "cart": cart.model_dump(mode="json")}), [], cart
                
            elif name == "view_cart":
                if not state.cart_id:
                    return json.dumps({"status": "success", "cart": {"items": [], "total_amount": 0}}), [], None
                cart = await self._clothing_app.get_cart(state.cart_id)
                return json.dumps({"status": "success", "cart": cart.model_dump(mode="json")}), [], cart
                
            elif name == "remove_from_cart":
                if not state.cart_id:
                    return json.dumps({"error": "Cart is empty"}), [], None
                cart = await self._clothing_app.remove_cart_item(state.cart_id, UUID(args["item_id"]))
                return json.dumps({"status": "success", "cart": cart.model_dump(mode="json")}), [], cart
                
            elif name == "clear_cart":
                if not state.cart_id:
                    return json.dumps({"error": "Cart is already empty"}), [], None
                cart = await self._clothing_app.clear_cart(state.cart_id)
                return json.dumps({"status": "success"}), [], cart
                
            return json.dumps({"error": f"Unknown tool: {name}"}), [], None
            
        except Exception as e:
            logger.exception("Tool execution failed")
            return json.dumps({"error": str(e)}), [], None

    async def handle_turn(self, message: str, state: ConversationState) -> tuple[str, list, Any]:
        system_context = json.dumps(
            {
                "shopping_stage": state.shopping_stage,
                "displayed_products": [
                    item.model_dump(mode="json") for item in state.displayed_products
                ],
                "selected_product": (
                    state.selected_product.model_dump(mode="json") if state.selected_product else None
                ),
                "has_cart": state.cart_id is not None,
            },
            default=str,
        )
        
        messages = [
            LLMMessage(role="system", content=self._prompt),
            LLMMessage(role="system", content=f"Context State: {system_context}")
        ]
        
        for msg in state.messages[-self._config.recent_message_limit :]:
            messages.append(LLMMessage(role=msg.role, content=msg.content))
            
        tools = self._get_tools()
        final_products = []
        final_cart = None
        
        for _ in range(4):
            response = await self._llm.generate_response(messages, tools=tools)
            
            if response.tool_calls:
                messages.append(LLMMessage(role="assistant", tool_calls=response.tool_calls))
                
                for tc in response.tool_calls:
                    res_str, prods, cart = await self._execute_tool(tc, state)
                    if prods:
                        final_products.extend(prods)
                    if cart:
                        final_cart = cart
                    
                    messages.append(LLMMessage(
                        role="tool",
                        name=tc["function"]["name"],
                        tool_call_id=tc.get("id", ""),
                        content=res_str
                    ))
                continue
                
            if response.content:
                return response.content, final_products, final_cart
                
        return "I'm having trouble processing that right now. Could we try again?", final_products, final_cart
