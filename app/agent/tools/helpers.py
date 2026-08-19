"""Helper utilities for category normalization and input parsing."""

import re
from typing import Optional, Any


def normalize_category_name(raw: str) -> str:
    raw_lower = raw.strip().lower()
    if raw_lower in ["all", "all products", "everything", "catalog", "تمام", "سب"]:
        return ""
    if any(k in raw_lower for k in ["t-shirt", "tshirt", "t shirt", "tee", "ٹی شرٹ", "ٹی شرٹس", "ٹی شرٹں"]):
        return "T-Shirts"
    elif any(k in raw_lower for k in ["polo", "پولو", "پولر", "poler", "polar"]):
        return "Polo Shirts"
    elif "active" in raw_lower or "ایکٹو" in raw_lower:
        return "Activewear"
    elif "gym" in raw_lower or "جم" in raw_lower:
        return "Gym Wear"
    elif "shirt" in raw_lower or "شرٹ" in raw_lower or "شرٹس" in raw_lower:
        return "Shirts"
    elif "trouser" in raw_lower or "ٹراؤزر" in raw_lower or "ٹراؤزرز" in raw_lower:
        return "Trousers"
    elif "pant" in raw_lower or "پینٹ" in raw_lower or "پینٹس" in raw_lower:
        return "Pants"
    elif any(k in raw_lower for k in ["hoodie", "jacket", "outerwear", "ہوڈی", "جیکٹ"]):
        return "Outerwear"
    elif any(k in raw_lower for k in ["traditional", "kurta", "shalwar", "شلوار", "کرتا", "روایتی"]):
        return "Traditional"
    elif "jean" in raw_lower or "جینز" in raw_lower or "جین" in raw_lower or "جیینز" in raw_lower:
        return "Jeans"
    return raw.strip().title()


def parse_categories_from_input(categories: Any = None, search_query: Optional[str] = None) -> list[str]:
    raw_items: list[str] = []
    if isinstance(categories, list):
        for item in categories:
            if isinstance(item, str):
                parts = re.split(r",|\band\b|&|اور|\+", item, flags=re.IGNORECASE)
                raw_items.extend(parts)
    elif isinstance(categories, str):
        parts = re.split(r",|\band\b|&|اور|\+", categories, flags=re.IGNORECASE)
        raw_items.extend(parts)

    text_to_parse = (search_query or "")
    if isinstance(categories, str):
        text_to_parse += " " + categories
    elif isinstance(categories, list):
        text_to_parse += " " + " ".join([c for c in categories if isinstance(c, str)])

    if text_to_parse:
        t_lower = text_to_parse.lower()
        if any(k in t_lower for k in ["polo", "پولو", "پولر", "poler", "polar"]):
            raw_items.append("Polo Shirts")
        if any(k in t_lower for k in ["jean", "جینز", "جین", "جیینز"]):
            raw_items.append("Jeans")
        if any(k in t_lower for k in ["t-shirt", "tshirt", "t shirt", "tee", "ٹی شرٹ", "ٹی شرٹس"]):
            raw_items.append("T-Shirts")
        if any(k in t_lower for k in ["trouser", "ٹراؤزر", "ٹراؤزرز"]):
            raw_items.append("Trousers")
        if any(k in t_lower for k in ["pant", "پینٹ", "پینٹس"]) and not any(k in t_lower for k in ["jean", "جینز", "ٹراؤزر"]):
            raw_items.append("Pants")
        if any(k in t_lower for k in ["hoodie", "jacket", "outerwear", "ہوڈی", "جیکٹ"]):
            raw_items.append("Outerwear")
        if any(k in t_lower for k in ["traditional", "kurta", "shalwar", "شلوار", "کرتا"]):
            raw_items.append("Traditional")

    normalized: list[str] = []
    for raw in raw_items:
        clean = raw.strip()
        if clean:
            norm = normalize_category_name(clean)
            if norm and norm not in normalized:
                normalized.append(norm)
    return normalized
# Multilingual size mapping covering standard international sizes, waist/chest numeric measurements, and Urdu script equivalents
SIZE_DICTIONARY: dict[str, str] = {
    "xs": "XS", "extra small": "XS", "ایکٹرا سمال": "XS",
    "s": "S", "small": "S", "اسمال": "S", "چھوٹا": "S",
    "m": "M", "medium": "M", "میڈیم": "M", "درمیانہ": "M",
    "l": "L", "large": "L", "لارج": "L", "بڑا": "L",
    "xl": "XL", "xlarge": "XL", "extra large": "XL", "x-large": "XL", "ایکسٹرا لارج": "XL",
    "xxl": "XXL", "xxlarge": "XXL", "double xl": "XXL", "2xl": "XXL", "ڈبل ایکسٹرا لارج": "XXL",
    "xxxl": "XXXL", "3xl": "XXXL", "triple xl": "XXXL", "ٹرپل ایکسٹرا لارج": "XXXL",
    "۲۸": "28", "۲۹": "29", "۳۰": "30", "۳۱": "31", "۳۲": "32", "۳۳": "33", "۳۴": "34", "۳۵": "35",
    "۳۶": "36", "۳۷": "37", "۳۸": "38", "۳۹": "39", "۴۰": "40", "۴۲": "42", "۴۴": "44", "۴۶": "46"
}

# Multilingual color dictionary mapping common color names across English and Urdu script to canonical color names
COLOR_DICTIONARY: dict[str, str] = {
    "blue": "Blue", "نیلا": "Blue", "نیلی": "Blue",
    "maroon": "Maroon", "عنابی": "Maroon", "سرخ": "Maroon",
    "black": "Black", "کالا": "Black", "کالی": "Black", "سیاہ": "Black",
    "white": "White", "سفید": "White",
    "beige": "Beige", "بیج": "Beige",
    "grey": "Grey", "gray": "Grey", "گری": "Grey", "سرمئی": "Grey",
    "red": "Red", "لال": "Red",
    "navy": "Navy", "نیوی": "Navy", "نیوی بلیو": "Navy",
    "green": "Green", "ہرا": "Green", "ہری": "Green", "سبز": "Green",
    "brown": "Brown", "براؤن": "Brown", "بھورا": "Brown",
    "khaki": "Khaki", "خاکی": "Khaki",
    "pink": "Pink", "گلابی": "Pink",
    "yellow": "Yellow", "پیلا": "Yellow", "پیلی": "Yellow",
    "purple": "Purple", "جامنی": "Purple",
    "orange": "Orange", "نارنجی": "Orange",
}


def normalize_size_label(raw: Any) -> str:
    """Generic size label normalizer for any product category (tops, bottoms, footwear, suits, etc.)."""
    if raw is None:
        return ""
    val_str = str(raw).strip()
    val_lower = val_str.lower()
    
    if val_lower in SIZE_DICTIONARY:
        return SIZE_DICTIONARY[val_lower]
        
    num_match = re.search(r'\b([0-9]{2,3})\b', val_str)
    if num_match:
        return num_match.group(1)
        
    return val_str.upper()


def normalize_color_name(raw: Any) -> str:
    """Generic color normalizer supporting English and Urdu script."""
    if raw is None:
        return ""
    val_str = str(raw).strip()
    val_lower = val_str.lower()
    
    if val_lower in COLOR_DICTIONARY:
        return COLOR_DICTIONARY[val_lower]
        
    return val_str.title()


def is_color_match(color_a: Optional[str], color_b: Optional[str]) -> bool:
    """Generic case-insensitive and multilingual color matching."""
    if not color_a or not color_b:
        return True
    norm_a = normalize_color_name(color_a).lower()
    norm_b = normalize_color_name(color_b).lower()
    return norm_a == norm_b or norm_a in norm_b or norm_b in norm_a


def is_size_match(size_a: Optional[str], size_b: Optional[str]) -> bool:
    """Generic size matching across all size formats."""
    if not size_a or not size_b:
        return True
    norm_a = normalize_size_label(size_a)
    norm_b = normalize_size_label(size_b)
    return norm_a == norm_b


VARIANT_SELECTION_TOKENS = {
    "s", "m", "l", "xl", "xxl", "3xl", "small", "medium", "large", "extra large", "x-large", "double xl", "2xl", "3xl",
    "اسمال", "میڈیم", "لارج", "بڑا", "درمیانہ", "چھوٹا", "ایکسٹرا لارج", "ڈبل ایکسٹرا لارج",
    "blue", "maroon", "black", "white", "beige", "grey", "gray", "red", "navy", "green", "brown", "khaki", "pink", "yellow", "purple", "orange",
    "نیلا", "نیلی", "عنابی", "مہرون", "مارون", "سرخ", "کالا", "کالی", "سیاہ", "سفید", "بیج", "گری", "سرمئی", "لال", "نیوی", "نیوی بلیو", "ہرا", "سبز", "براؤن", "بھورا", "خاکی", "گلابی", "پیلا", "پیلی", "جامنی", "نارنجی",
    "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "42", "44", "46",
    "۲۸", "۲۹", "۳۰", "۳۱", "۳۲", "۳۳", "۳۴", "۳۵", "۳۶", "۳۷", "۳۸", "۳۹", "۴۰", "۴۲", "۴۴", "۴۶",
    "size", "color", "سائز", "کلر", "اس", "میں", "اور"
}


def is_variant_selection_reply(user_message: str) -> bool:
    """Return True if user message contains variant parameters (color/size/numeric measurement) for an active product."""
    msg_lower = user_message.lower()
    
    # Check for any size or color mention in English or Urdu
    size_found = bool(re.search(r'\b(s|m|l|xl|xxl|small|medium|large|اسمال|میڈیم|لارج|سائز|\d{2})\b', msg_lower))
    color_found = bool(re.search(r'\b(blue|maroon|black|white|beige|grey|red|navy|green|brown|نیلا|عنابی|مہرون|مارون|سیاہ|سفید|نیوی|کلر)\b', msg_lower))
    
    if size_found or color_found:
        return True
        
    words = [w.strip().lower() for w in re.split(r'\s+|,', user_message) if w.strip()]
    if not words:
        return False
    matched = [w for w in words if w in VARIANT_SELECTION_TOKENS]
    return len(matched) > 0 and (len(words) <= 5 or len(matched) / len(words) >= 0.3)
