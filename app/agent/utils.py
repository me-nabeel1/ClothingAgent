"""Reusable utility helpers for single agent operations, context formatting, and tool execution."""

import logging
import re
from typing import Optional, Any

from app.agent.state import ConversationState
from app.agent.registry import ToolSpec
from app.agent.checker import ParameterRequirementsChecker
from app.agent.intent import StructuredIntent
from app.clients.clothing_app.schemas import StoreContext

logger = logging.getLogger(__name__)


def clean_reply_formatting(reply: str) -> str:
    """Post-processing filter to strip forbidden currency symbols (₹, Rs, PKR, .00), eliminate Devanagari Hindi characters, Roman Urdu leaks, and enforce whole integer prices with rupees/روپے labels."""
    if not reply:
        return reply

    # 1. Clean decimal .00 endings (e.g. 1500.00 -> 1500)
    reply = re.sub(r'\b([0-9]+)\.00\b', r'\1', reply)

    # 2. Strip Devanagari Hindi script characters if any slip through
    reply = re.sub(r'[\u0900-\u097F]+', '', reply)

    # 3. Replace Indian Rupee symbol (₹) or ₹ 1500 -> 1500 rupees
    reply = re.sub(r'₹\s*([0-9]+)', r'\1 rupees', reply)
    reply = re.sub(r'₹', '', reply)

    # 4. Replace Rs. 1500 / Rs 1500 / PKR 1500 -> 1500 rupees
    reply = re.sub(r'(?:Rs\.?|PKR)\s*([0-9]+)', r'\1 rupees', reply)

    # 5. Remove duplicate currency labels (e.g. 1500 rupees rupees -> 1500 rupees)
    reply = re.sub(r'\b(rupees|روپے)\s+\1\b', r'\1', reply)

    # 6. Replace common Roman Urdu lead phrases if LLM leaked them
    roman_urdu_fixes = [
        (r'\bAap ke cart me\b', 'In your cart', re.IGNORECASE),
        (r'\bAap ka\b', 'Your', re.IGNORECASE),
        (r'\bAap ki\b', 'Your', re.IGNORECASE),
        (r'\bAap ke\b', 'Your', re.IGNORECASE),
        (r'\bPehla option\b', 'Option 1', re.IGNORECASE),
        (r'\bDusra option\b', 'Option 2', re.IGNORECASE),
        (r'\bTeesra option\b', 'Option 3', re.IGNORECASE),
        (r'\bChautha option\b', 'Option 4', re.IGNORECASE),
        (r'\bShukriya\b', 'Thank you', re.IGNORECASE),
        (r'\bBatao\b', 'Tell me', re.IGNORECASE),
        (r'\bKardo\b', 'Do it', re.IGNORECASE),
    ]
    for pattern, replacement, flags in roman_urdu_fixes:
        reply = re.sub(pattern, replacement, reply, flags=flags)

    return reply


def format_store_context_str(context: StoreContext) -> str:
    """Format StoreContext into a standard text summary for LLM prompt context."""
    return (
        f"Brand/Store Context:\n"
        f"- Brand Name: {context.store_name}\n"
        f"- Available Categories: {context.categories}\n"
        f"- Available Product Types: {context.product_types}\n"
        f"- Available Occasions: {context.occasions}\n"
        f"- Available Colors: {context.colors}\n"
        f"- Available Sizes: {context.sizes}\n"
    )


def is_greeting_or_reset_message(user_message: str) -> tuple[bool, bool]:
    """Check if the user message is an opening greeting or an explicit session reset request."""
    msg_clean = user_message.strip().lower()
    greetings = {"hi", "hello", "hey", "ہیلو", "سلام", "ہیلو!", "سلام!", "good morning", "good evening", "good day", "as-salamu alaykum", "assalam o alaikum"}
    is_greeting = msg_clean in greetings or any(msg_clean.startswith(g) for g in ["hi ", "hello ", "hey ", "ہیلو ", "سلام "])
    reset_keywords = {"reset", "reset session", "start fresh", "start over", "new chat", "clear session", "restart", "نئی سیشن", "نیا سیشن", "شروع سے", "دوبارہ شروع کرو"}
    is_reset = msg_clean in reset_keywords
    return is_greeting, is_reset


def build_concierge_greeting(store_name: str, user_message: str) -> str:
    """Build brand concierge opening greeting in Urdu script or English based on user query language."""
    if any(ch in user_message for ch in ["اردو", "سلام", "ہیلو", "نیا", "شروع"]):
        return f"ہیلو! {store_name} میں خوش آمدید۔ بطور آپ کے پرسنل سیلز کنسیئرج، آج آپ اپنی شخصیت کو نکھارنے کے لیے کون سا لباس یا اسٹائل پہننا چاہتے ہیں؟"
    return f"Hello! Welcome to {store_name}. As your personal AI Sales Concierge, what style or outfit are you looking to wear today to elevate your personality and boost your confidence?"


async def execute_validated_tool(spec: ToolSpec, args: dict, state: ConversationState) -> str:
    """Validate tool requirements via ParameterRequirementsChecker and execute the tool handler safely."""
    try:
        validation_error = await ParameterRequirementsChecker.check(spec, args, state)
        if validation_error:
            return validation_error

        payload = spec.payload_model(**args)
        result = await spec.handler(state, payload)
        return result if isinstance(result, str) else str(result)
    except Exception as exc:
        logger.error(f"Error executing tool {spec.name}: {exc}")
        return f"Error executing {spec.name}: {str(exc)}"


def args_from_intent(intent: StructuredIntent, state: ConversationState) -> dict:
    """Extract arguments dictionary from StructuredIntent for tool payload instantiation."""
    args = {}
    filters = intent.search_overrides or intent.filters
    if filters:
        if filters.categories:
            args["categories"] = filters.categories
            args["category_name"] = filters.categories[0]
        if filters.product_types: args["product_types"] = filters.product_types
        if filters.occasions: args["occasions"] = filters.occasions
        if filters.colors:
            args["colors"] = filters.colors
            args["color"] = filters.colors[0]
        if filters.excluded_colors: args["excluded_colors"] = filters.excluded_colors
        if filters.sizes:
            args["size_mapping"] = filters.sizes
            if isinstance(filters.sizes, dict) and filters.sizes:
                args["size"] = next(iter(filters.sizes.values()))
            elif isinstance(filters.sizes, list) and filters.sizes:
                args["size"] = str(filters.sizes[0])
            elif isinstance(filters.sizes, str):
                args["size"] = filters.sizes
        if filters.materials: args["materials"] = filters.materials
        if filters.fits: args["fits"] = filters.fits
        if filters.budget:
            if getattr(filters.budget, 'minimum', None) is not None: args["minimum_price"] = filters.budget.minimum
            if getattr(filters.budget, 'maximum', None) is not None: args["maximum_price"] = filters.budget.maximum
        if filters.branch: args["branch_code"] = filters.branch
        if filters.specific_article: args["article_code"] = filters.specific_article
        
    if intent.search_query:
        args["query_text"] = intent.search_query
        
    if intent.selected_product_index is not None:
        args["selected_product_index"] = intent.selected_product_index
        if 1 <= intent.selected_product_index <= len(state.displayed_products):
            args["product_id"] = state.displayed_products[intent.selected_product_index - 1].product_id
            args["item_id"] = state.displayed_products[intent.selected_product_index - 1].product_id
            
    if intent.quantity:
        args["quantity"] = intent.quantity
        
    if intent.delivery_info:
        if intent.delivery_info.customer_name: args["customer_name"] = intent.delivery_info.customer_name
        if intent.delivery_info.phone: args["phone"] = intent.delivery_info.phone
        if intent.delivery_info.delivery_address: args["delivery_address"] = intent.delivery_info.delivery_address
        if intent.delivery_info.city: args["city"] = intent.delivery_info.city
        if intent.delivery_info.delivery_notes: args["delivery_notes"] = intent.delivery_info.delivery_notes
        
    return args
