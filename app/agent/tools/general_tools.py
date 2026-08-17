"""General store tool handlers for promotions, store availability, and offers."""

import logging
from typing import Optional, Any

from app.agent.state import ConversationState
from app.agent.schemas import GetPromotionsPayload, CheckAvailabilityPayload
from app.clients.clothing_app.client import ClothingAppClient

logger = logging.getLogger(__name__)


class GeneralToolsMixin:
    """General store information and promotions capabilities."""

    _client: ClothingAppClient

    async def get_promotions(self, state: ConversationState, payload: GetPromotionsPayload) -> str:
        """Fetch active promotions and format them as a string."""
        state.clear_cards()
        promos = await self._client.get_promotions()
        if not promos:
            return "No exclusive offers or promotions are currently running."
        
        lines = ["Currently active promotions:"]
        for p in promos:
            details = f"- {p.offer_name} (Code: {p.offer_code}): {p.description or 'Special offer'}"
            if p.discount_percentage:
                details += f" ({p.discount_percentage}% off)"
            elif p.discount_amount:
                details += f" (Rs {p.discount_amount} off)"
            lines.append(details)
        return "\n".join(lines)

    async def check_availability(self, state: ConversationState, payload: CheckAvailabilityPayload) -> str:
        state.clear_cards()
        details = await self._client.get_product(payload.product_id)
        if not details or not details.product or not details.product.variants:
            return "Product not found or has no variants."
            
        matching = []
        for v in details.product.variants:
            if payload.color and v.color.lower() != payload.color.lower():
                continue
            if payload.size and v.size.lower() != payload.size.lower():
                continue
            matching.append(v)
            
        if not matching:
            return "No matching variants found for that color/size."
            
        variant_id = matching[0].variant_id
        
        branch_id = None
        if payload.branch:
            branches = await self._client.list_branches()
            for b in branches:
                if payload.branch.lower() in b.name.lower():
                    branch_id = b.branch_id
                    break
        
        if not branch_id and state.branch_preference:
            branches = await self._client.list_branches()
            for b in branches:
                if state.branch_preference.lower() in b.name.lower():
                    branch_id = b.branch_id
                    break
                    
        if not branch_id:
            branches = await self._client.list_branches()
            if branches:
                branch_id = branches[0].branch_id
                
        if not branch_id:
            return "Could not determine a store branch to check."
            
        avail = await self._client.get_availability(variant_id, branch_id)
        if avail and avail.is_available:
            return f"Yes, that's in stock. {avail.available_quantity} available."
        return "Sorry, that item is currently out of stock at this branch."
