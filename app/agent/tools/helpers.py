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
