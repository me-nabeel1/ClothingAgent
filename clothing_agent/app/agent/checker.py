from typing import Optional, Any
from app.agent.state import ConversationState
from app.agent.schemas import GetProductDetailsPayload
from app.agent.tools import AgentTools

class ParameterRequirementsChecker:
    """Checks if tool actions have their primary required parameters before execution."""

    @staticmethod
    async def check_action_requirements(
        func_name: str, 
        args: dict[str, Any], 
        state: ConversationState, 
        tools: AgentTools
    ) -> Optional[str]:
        """
        Returns an error string for the LLM if parameters are missing,
        or None if all required parameters are present.
        """
        if func_name == "add_cart_item":
            color = args.get("color")
            size = args.get("size")
            
            # Resolve product ID
            product_id = args.get("product_id") or state.selected_product_id
            if not product_id and args.get("selected_product_index") is not None:
                idx = args.get("selected_product_index")
                if 1 <= idx <= len(state.displayed_products):
                    product_id = state.displayed_products[idx - 1].product_id
            if not product_id and state.displayed_products:
                product_id = state.displayed_products[0].product_id
                
            if not product_id:
                return "MISSING PARAMETERS: Cannot determine which product to add. INSTRUCTION: Ask the user which product they want to add."
                
            # Fetch product to check variants
            details = await tools.get_product_details(GetProductDetailsPayload(product_id=product_id), state)
            if details and details.product and details.product.variants:
                p = details.product
                available_colors = sorted(list(set(v.color for v in p.variants if v.is_available)))
                available_sizes = sorted(list(set(v.size for v in p.variants if v.is_available)))
                
                # If the product actually has multiple options, enforce them
                needs_color = len(available_colors) > 0
                needs_size = len(available_sizes) > 0
                
                missing = []
                if needs_color and not color: missing.append("color")
                if needs_size and not size: missing.append("size")
                
                if missing:
                    color_str = f"Available Colors: {', '.join(available_colors)}." if available_colors else ""
                    size_str = f"Available Sizes: {', '.join(available_sizes)}." if available_sizes else ""
                    return f"MISSING PARAMETERS for add_cart_item: Requires explicitly stated {', '.join(missing)} for '{p.product_name}'. {color_str} {size_str} INSTRUCTION: Tell the user you need them to select the {', '.join(missing)} before adding to cart."
                    
        elif func_name == "place_order":
            missing = []
            if not args.get("customer_name"): missing.append("customer_name")
            if not args.get("phone"): missing.append("phone")
            if not args.get("delivery_address"): missing.append("delivery_address")
            if not args.get("city"): missing.append("city")
            
            if missing:
                return f"MISSING PARAMETERS for place_order: Requires {', '.join(missing)}. INSTRUCTION: Ask the user to provide their {', '.join(missing)} to complete the order."
                
        elif func_name == "explore_category":
            if not args.get("category_name"):
                return "MISSING PARAMETERS for explore_category: Requires 'category_name'. INSTRUCTION: Ask the user which category they want to explore."

        # If everything is complete, return None to allow execution
        return None
