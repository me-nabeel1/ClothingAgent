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


def detect_input_language(user_message: str) -> str:
    """
    Detect whether user message is Urdu (Urdu Script or Roman Urdu transcript) vs English.
    Returns: 'ur' for Urdu, 'en' for English.
    """
    if not user_message:
        return 'en'

    # 1. Check for Urdu Script characters (\u0600-\u06FF)
    if any('\u0600' <= ch <= '\u06ff' for ch in user_message):
        return 'ur'

    # 2. Check for distinctive Roman Urdu keywords (from STT voice transcripts)
    distinctive_roman_urdu_keywords = {
        "mujhe", "mujhy", "dikhao", "dikhaye", "dikhayen", "kardo",
        "pehla", "dusra", "teesra", "chautha", "yeh", "woh", "batao", "bataen", "shukriya",
        "konsa", "konsi", "mangwana", "bhej", "chahiye", "paisa", "rupay", "rupee", "karo",
        "salaam", "salam", "shukria", "bhejo", "dikha", "dikhaen"
    }
    words = set(re.findall(r'\b[a-zA-Z]{3,}\b', user_message.lower()))
    if len(words.intersection(distinctive_roman_urdu_keywords)) >= 1:
        return 'ur'

    return 'en'


def clean_reply_formatting(reply: str) -> str:
    """Post-processing filter to format replies for clean Text-to-Speech (TTS) voice playback and strip forbidden currency/markdown/emoji symbols."""
    if not reply:
        return reply

    # 1. Clean decimal .00 endings (e.g. 1500.00 -> 1500)
    reply = re.sub(r'\b([0-9]+)\.00\b', r'\1', reply)

    # 2. Strip Devanagari Hindi script characters if any slip through
    reply = re.sub(r'[\u0900-\u097F]+', '', reply)

    # 3. Clean emoji number blocks (1️⃣, 2️⃣, 3️⃣, etc.) -> plain numbers (1., 2., 3.)
    emoji_numbers = {
        "1️⃣": "1.", "2️⃣": "2.", "3️⃣": "3.", "4️⃣": "4.", "5️⃣": "5.",
        "6️⃣": "6.", "7️⃣": "7.", "8️⃣": "8.", "9️⃣": "9.", "🔟": "10."
    }
    for emo, num in emoji_numbers.items():
        reply = reply.replace(emo, num)

    # 4. Clean bracketed numbers like [1], [2] -> 1., 2.
    reply = re.sub(r'\[([0-9]+)\]', r'\1.', reply)

    # 5. Language-aware currency symbol replacement (Rs, Rs., PKR, ₹)
    is_urdu = any('\u0600' <= ch <= '\u06ff' for ch in reply)
    curr_label = "روپے" if is_urdu else "rupees"

    # Replace Indian Rupee symbol (₹)
    reply = re.sub(r'₹\s*([0-9,]+)', rf'\1 {curr_label}', reply)
    reply = re.sub(r'₹', '', reply)

    # Replace Rs / Rs. / PKR before OR after price digits
    reply = re.sub(r'(?:Rs\.?|PKR)\s*([0-9,]+)', rf'\1 {curr_label}', reply, flags=re.IGNORECASE)
    reply = re.sub(r'([0-9,]+)\s*(?:Rs\.?|PKR)', rf'\1 {curr_label}', reply, flags=re.IGNORECASE)
    reply = re.sub(r'\b(?:Rs\.?|PKR)\b', curr_label, reply, flags=re.IGNORECASE)

    # 6. Remove duplicate currency labels (e.g. 1500 rupees rupees -> 1500 rupees / 1500 روپے روپے -> 1500 روپے)
    reply = re.sub(r'\b(rupees|روپے)\s+\1\b', r'\1', reply)

    # 7. Replace common Roman Urdu lead phrases if LLM leaked them
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

    # 8. Strip Markdown syntax symbols (*, #, `, ~) for smooth TTS voice reading
    reply = re.sub(r'\*+([^*]+)\*+', r'\1', reply)
    reply = re.sub(r'#+\s*', '', reply)
    reply = re.sub(r'`+([^`]+)`+', r'\1', reply)
    reply = re.sub(r'~+([^~]+)~+', r'\1', reply)
    reply = re.sub(r'^\s*[\*\-\+]\s+', '', reply, flags=re.MULTILINE)

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
