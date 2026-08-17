"""Structured intent extraction using the single LLM."""

from __future__ import annotations

import logging
from typing import Optional, Any
from pydantic import BaseModel, Field

from app.agent.state import ConversationState, Budget
from app.clients.clothing_app.schemas import StoreContext
from app.llm.client import LLMClient, LLMMessage

logger = logging.getLogger(__name__)


class ExtractedFilters(BaseModel):
    """Shopping constraints extracted from natural language."""
    categories: Optional[list[str]] = Field(default=None)
    product_types: Optional[list[str]] = Field(default=None)
    occasions: Optional[list[str]] = Field(default=None)
    colors: Optional[list[str]] = Field(default=None)
    excluded_colors: Optional[list[str]] = Field(default=None)
    sizes: Optional[dict[str, str]] = Field(default=None, description="e.g. {'shirt': 'L', 'pants': '34'}")
    materials: Optional[list[str]] = Field(default=None)
    fits: Optional[list[str]] = Field(default=None)
    budget: Optional[Budget] = Field(default=None)
    branch: Optional[str] = None
    specific_article: Optional[str] = Field(None, description="Exact article code if mentioned (e.g., NS-SH-001)")


class DeliveryInfoExtraction(BaseModel):
    """Extracted delivery fields for order placement."""
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    delivery_address: Optional[str] = None
    city: Optional[str] = None
    delivery_notes: Optional[str] = None


class StructuredIntent(BaseModel):
    """The complete intention of the customer's message."""
    intent: str = Field(description="One of: 'search', 'get_details', 'add_to_cart', 'remove_cart', 'show_cart', 'checkout', 'place_order', 'general_chat', 'clear_preferences', 'get_promotions'")
    clear_previous_preferences: bool = Field(False, description="Set to true if the user is completely changing the topic or abandoning a previous search.")
    filters: Optional[ExtractedFilters] = Field(default=None, description="Persistent filters to apply or merge based on explicit user preference statements")
    search_overrides: Optional[ExtractedFilters] = Field(default=None, description="Temporary filters for the current search (e.g. 'Show me blue shirts' vs 'I prefer blue')")
    delivery_info: Optional[DeliveryInfoExtraction] = Field(default=None, description="Extracted delivery details when the user provides them during checkout")
    selected_product_index: Optional[int] = Field(None, description="1-based index of product if user is referring to a single product in a recently displayed product list")
    selected_product_indices: list[int] = Field(default_factory=list, description="List of all 1-based product indices the user selected or showed interest in (e.g. [2] or [2, 4])")
    search_query: Optional[str] = Field(None, description="Free text semantic search if specific vocabulary doesn't match")
    quantity: Optional[int] = Field(1, description="Quantity for cart actions")
    order_confirmed: Optional[bool] = Field(None, description="True if the user explicitly confirms they want to place the order after seeing the total")


class PlannedStep(BaseModel):
    """One action within a (possibly multi-action) customer turn, in the
    order it should execute."""
    step_id: str = Field(description="e.g. 'step_1', 'step_2' — referenced by later steps' depends_on")
    intent: StructuredIntent
    depends_on: str | None = Field(
        default=None,
        description="step_id of a prior step that must complete AND pass its "
                     "verify check before this step is allowed to run"
    )
    verify: str | None = Field(
        default=None,
        description="Name of a postcondition to check on this step's own "
                     "result before any step depending on it is allowed to "
                     "run. Use short fixed identifiers, e.g. 'cart_is_empty'. "
                     "None if no check is needed."
    )


class IntentPlan(BaseModel):
    """Full extraction result for one customer turn. A single-intent
    message must still produce a plan with exactly one PlannedStep — do not
    special-case single-intent handling separately from multi-intent
    handling anywhere downstream."""
    steps: list[PlannedStep] = Field(min_length=1)
    reasoning: str | None = Field(
        default=None,
        description="Short internal rationale for the plan ordering. For "
                     "logs only. NEVER shown to the customer."
    )


class IntentExtractor:
    """Extracts structured meaning from customer messages."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    async def extract(
        self,
        user_input: str,
        state: ConversationState,
        context: StoreContext,
    ) -> IntentPlan:
        """Parse user input into an IntentPlan using store vocabulary."""
        from app.llm.prompts import SYSTEM_PROMPT_ROUTING
        
        system_instruction = (
            f"{SYSTEM_PROMPT_ROUTING}\n\n"
            f"You are a routing and extraction engine for {context.store_name}.\n"
            "Analyze the user's message and current state, then output a JSON object.\n\n"
            "Current state summary:\n"
            f"- Stage: {state.conversation_stage}\n"
            f"- Intent: {state.current_intent}\n"
            f"- Categories: {state.categories}\n"
            f"- Occasions: {state.occasions}\n"
            f"- Colors: {state.preferred_colors}\n"
            f"- Last Displayed Products: {[p.product_name for p in state.displayed_products]}\n\n"
            "Available Vocabulary (Must match EXACTLY if used):\n"
            f"Categories: {context.categories}\n"
            f"Product Types: {context.product_types}\n"
            f"Occasions: {context.occasions}\n"
            f"Colors: {context.colors}\n"
            f"Sizes: {context.sizes}\n"
            f"Materials: {context.supported_attributes}\n"
            f"Branches: {[b.branch_code for b in context.branches]}\n\n"
            "Rules:\n"
            "1. If the user asks to see products, browse collections, or explore categories, intent is 'search' or 'explore_category'. Provide the filters.\n"
            "2. Product Selection & Detail Intent (CRITICAL): If the user selects a product option, shortlists an item, or asks for details about a displayed product (e.g., 'option 4 looks good', '2nd one', 'tell me about 3rd', '4th option seems fine'), intent MUST be 'get_details' or 'add_to_cart'. NEVER classify selecting or discussing an option as 'search'!\n"
            "3. If the user explicitly asks to add a product to the cart, intent MUST be 'add_to_cart'. Place mentioned attributes in 'search_overrides'.\n"
            "4. If the user wants to review their cart, intent is 'show_cart'. If they want to begin checkout, intent is 'checkout'. If the user explicitly confirms they want to finalize/place the order (e.g. saying 'yes' when asked to place order), intent MUST be 'place_order' and set 'order_confirmed' to true.\n"
            "5. Map words to the exact vocabulary above. For example, 'wedding' -> 'wedding'.\n"
            "6. 'selected_product_index' should be a number (1, 2, 3) if they refer to 'the first one', 'option 4', etc.\n"
            "7. Differentiate explicit preferences from temporary searches:\n"
            "   - If the user explicitly states a preference (e.g., 'I like black', 'My budget is 5000'), put those in 'filters'.\n"
            "   - If the user asks for a temporary search (e.g., 'Show me blue shirts'), put those in 'search_overrides'.\n"
            "   - Do not overwrite persistent preferences with temporary search terms.\n"
            "   - CRITICAL: If the user mentions a category (e.g., 'pants', 't-shirts', 'jeans'), you MUST place the exact matching vocabulary word (e.g. 'Pants', 'T-Shirts') into 'categories' under 'search_overrides' (or 'filters' if persistent).\n"
            "8. Context Preservation (CRITICAL): If the user makes a follow-up refinement (e.g., 'show me cheaper', 'do you have IT in maroon', 'larger size') without explicitly starting a new search, you MUST infer ALL their previously active search constraints (Category, Color, Size, etc.) from the 'Current state summary' and include them in 'search_overrides', modifying ONLY the specific attribute they asked to refine (e.g., lower the budget, change the color). Never drop existing context unless the user explicitly changes it.\n"
            "9. Topic Switching: If the user completely changes the topic (e.g. from looking for 'shoes' to 't-shirts') OR explicitly abandons a previous search that yielded no results (e.g., agent says 'I couldn't find anything for 500' and user says 'okay show me t-shirts instead'), you MUST set 'clear_previous_preferences' to true to reset their persistent filters before starting the new search.\n"
            "10. Clarification Context (CRITICAL): If the Current Intent is 'add_to_cart' or 'get_details' and the user provides ONLY a size, color, index, or simple clarification (e.g., 'brown', 'large', 'l beige', 'the blue one'), you MUST keep the intent as 'add_to_cart' or 'get_details'. NEVER return 'search' in this scenario! Place the extracted attributes into 'search_overrides'.\n"
            "11. Promotions: If the user asks for current offers, discounts, exclusive offers, or promotions, intent MUST be 'get_promotions'.\n"
            "11. Checkout Form Submission: If the user message starts with 'Place order with corrected details:' (or similar structured format), you MUST set intent to 'place_order' and set 'order_confirmed' to true. Map the Name, Phone, City, and Address EXACTLY as provided in the message.\n"
            "12. Delivery Info Extraction: Be careful not to mix up city and address. A known major city goes to 'city'. Specific local areas, villages, or street names (e.g., 'dinga') should go to 'delivery_address' or 'delivery_notes'.\n"
            "13. Semantic Search (CRITICAL): ALWAYS extract the main items the user is looking for (e.g., 'casual shirt', 'black trousers', 'gym clothes') into 'search_query' even if you also map it to a category or other filters. This ensures the search engine has semantic context.\n"
            "14. Multi-Intent Planning (CRITICAL): If the customer's message contains\n"
            "    more than one distinct action (for example: \"empty my cart and show me\n"
            "    cheaper t-shirts\"), break it into ordered `steps`. A single-intent\n"
            "    message still produces `steps` with exactly one entry — never omit the\n"
            "    list structure.\n"
            "\n"
            "    Ordering rule: order steps by logical dependency, not by the order\n"
            "    the customer happened to phrase them in. If a later step's correct\n"
            "    behavior depends on an earlier step's outcome (e.g. a cart-based search\n"
            "    needs the cart to already be cleared), the earlier step must come first\n"
            "    and the later step's `depends_on` must reference it.\n"
            "\n"
            "    Context carryover rule: every step must inherit relevant context from\n"
            "    earlier in the conversation AND from earlier steps in the same plan.\n"
            "    If the customer was browsing a category earlier (e.g. T-Shirts) and a\n"
            "    later step in this same message says \"cheaper options\" without\n"
            "    re-stating the category, that step's search filters MUST still include\n"
            "    the earlier category — do not produce an unscoped, category-less search\n"
            "    just because this particular sentence didn't repeat it.\n"
            "\n"
            "    Verification rule: set `verify` to a short fixed identifier (for\n"
            "    example \"cart_is_empty\") on any step whose success must be confirmed\n"
            "    before a dependent step is allowed to run. Leave `verify` as null when\n"
            "    no such check is needed.\n"
            "\n"
            "    Never invent extra steps the customer didn't ask for. Never merge two\n"
            "    genuinely distinct requested actions into one step to save an entry.\n"
            "\n"
            "    CRITICAL: The `intent` field inside each `step` MUST be a full JSON object matching the StructuredIntent schema, NOT just a string.\n"
        )

        messages = [
            LLMMessage(role="system", content=system_instruction),
            LLMMessage(role="user", content=user_input)
        ]
        
        logger.info("extracting_intent", extra={"event": "extracting_intent", "user_input": user_input})
        result = await self._llm.generate_structured(messages, IntentPlan)
        logger.info(
            "intent_plan_extracted",
            extra={
                "event": "intent_plan_extracted",
                "step_count": len(result.steps),
                "intents": [step.intent.intent for step in result.steps],
                "has_dependencies": any(step.depends_on for step in result.steps),
            },
        )
        return result
