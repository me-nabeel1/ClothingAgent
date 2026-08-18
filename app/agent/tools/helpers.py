"""Helper utilities for category normalization and input parsing."""

import re
from typing import Optional, Any


def normalize_category_name(raw: str) -> str:
    raw_lower = raw.strip().lower()
    if raw_lower in ["all", "all products", "everything", "catalog", "تمام", "سب"]:
        return ""
    if any(k in raw_lower for k in ["t-shirt", "tshirt", "t shirt", "tee", "ٹی شرٹ", "ٹی شرٹس", "ٹی شرٹں"]):
        return "T-Shirts"
    elif "polo" in raw_lower or "پولو" in raw_lower:
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
    elif "jean" in raw_lower or "جینز" in raw_lower or "جین" in raw_lower:
        return "Jeans"
    return raw.strip().title()


def parse_categories_from_input(categories: Any = None, search_query: Optional[str] = None) -> list[str]:
    raw_items: list[str] = []
    if isinstance(categories, list):
        for item in categories:
            if isinstance(item, str):
                parts = re.split(r",|\band\b|&|اور", item, flags=re.IGNORECASE)
                raw_items.extend(parts)
    elif isinstance(categories, str):
        parts = re.split(r",|\band\b|&|اور", categories, flags=re.IGNORECASE)
        raw_items.extend(parts)

    if not raw_items and search_query:
        sq_lower = search_query.lower()
        if any(k in sq_lower for k in ["t-shirt", "tshirt", "t shirt", "tee", "ٹی شرٹ", "ٹی شرٹس"]):
            raw_items.append("T-Shirts")
        elif "shirt" in sq_lower or "شرٹ" in sq_lower or "شرٹس" in sq_lower:
            raw_items.append("Shirts")
        if "trouser" in sq_lower or "ٹراؤزر" in sq_lower:
            raw_items.append("Trousers")
        if "pant" in sq_lower or "پینٹ" in sq_lower or "پینٹس" in sq_lower:
            raw_items.append("Pants")
        if any(k in sq_lower for k in ["hoodie", "jacket", "outerwear", "ہوڈی", "جیکٹ"]):
            raw_items.append("Outerwear")
        if any(k in sq_lower for k in ["traditional", "kurta", "shalwar", "شلوار", "کرتا"]):
            raw_items.append("Traditional")
        if "jean" in sq_lower or "جینز" in sq_lower:
            raw_items.append("Jeans")

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
