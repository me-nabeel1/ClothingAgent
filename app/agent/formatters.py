"""Hardcoded response schema formatters for product catalog listing and product details."""

from typing import Any


def translate_category_to_urdu(cat_name: str) -> str:
    """Translate category names to Urdu script for display headers."""
    cat_lower = cat_name.strip().lower()
    mapping = {
        "t-shirts": "ٹی شرٹس",
        "t-shirt": "ٹی شرٹس",
        "tshirt": "ٹی شرٹس",
        "shirts": "شرٹس",
        "shirt": "شرٹس",
        "casual cotton shirts": "کاٹن شرٹس",
        "formal dress shirts": "فارمل ڈریس شرٹس",
        "polo shirts": "پولو شرٹس",
        "pants": "پینٹس",
        "pant": "پینٹس",
        "jeans": "جینز",
        "trousers": "ٹراؤزرز",
        "track pants": "ٹریک پینٹس",
        "shorts": "شارٹس",
        "activewear": "ایکٹو ویئر",
        "outerwear": "جیکٹس اور آؤٹر ویئر",
        "jackets": "جیکٹس",
        "hoodies": "ہوڈیز",
        "sweatshirts": "سویٹ شرٹس",
        "blazers": "بلیزرز",
        "suits": "فارمل سوٹس",
        "tuxedo": "تکسیڈو",
    }
    return mapping.get(cat_lower, cat_name.strip().title())


def format_product_listing_schema(
    grouped_products: dict[str, list[Any]],
    user_lang: str = "en",
    intro_message: str | None = None,
    followup_message: str | None = None
) -> str:
    """
    Format product listing using hardcoded schema:
    [Nice smooth opening reply]

    ---- Category/Subcategory Name ----
    1 Product Name - Price rupees.
    2 Product Name - Price rupees.
    3 Product Name - Price rupees.

    [Nice follow-up message]
    """
    if user_lang == "ur":
        intro = intro_message or "ٹھیک ہے، آپ کے لیے ہماری کلیکشن میں سے کچھ بہترین مصنوعات موجود ہیں۔"
        followup = followup_message or "ان میں سے کون سا لباس آپ کو پسند آیا، یا کیا آپ کسی کی مزید تفصیلات دیکھنا چاہتے ہیں یا اپنے بیگ میں شامل کرنا چاہتے ہیں؟"
        currency = "روپے"
    else:
        intro = intro_message or "Okay, here are some great products curated for you."
        followup = followup_message or "Which one of these do you like, or would you like to see more details or add to your bag?"
        currency = "rupees"

    lines = [intro]
    opt_idx = 1

    for cat_name, items in grouped_products.items():
        clean_cat = cat_name.strip().replace("_", " ").replace("-", " ")
        clean_cat = " ".join(clean_cat.split())
        if user_lang == "ur":
            header_title = translate_category_to_urdu(clean_cat)
        else:
            header_title = clean_cat.title()

        lines.append(f"\n---- {header_title} ----")
        for p in items[:3]:
            price_int = int(float(p.final_price)) if p.final_price is not None else 0
            lines.append(f"{opt_idx} {p.product_name} - {price_int} {currency}.")
            opt_idx += 1

    lines.append(f"\n{followup}")
    return "\n".join(lines)


def format_product_details_schema(
    product: Any,
    user_lang: str = "en",
    intro_message: str | None = None,
    followup_message: str | None = None
) -> str:
    """
    Format product details using hardcoded schema:
    [Nice smooth opening reply]

    Product details:
    name: [Product Name]
    size: [Available Sizes]
    color: [Available Colors]
    price: [Price] rupees

    [Ask action / follow-up question]
    """
    price_int = int(float(product.final_price)) if product.final_price is not None else 0
    all_avail = [v for v in (product.variants or []) if v.is_available]
    colors_str = ", ".join(sorted(list(set(v.color for v in all_avail)))) if all_avail else "Various"
    sizes_str = ", ".join(sorted(list(set(v.size for v in all_avail)))) if all_avail else "Various"

    if user_lang == "ur":
        intro = intro_message or f"{product.product_name} کی تفصیلات پیش ہیں۔"
        header = "Product details:"
        label_name = "name:"
        label_size = "size:"
        label_color = "color:"
        label_price = "price:"
        currency = "روپے"
        followup = followup_message or "آپ کون سا سائز اور رنگ منتخب کرنا چاہیں گے تاکہ میں اسے آپ کے بیگ میں شامل کر سکوں؟"
    else:
        intro = intro_message or f"Here are the complete details for {product.product_name}."
        header = "Product details:"
        label_name = "name:"
        label_size = "size:"
        label_color = "color:"
        label_price = "price:"
        currency = "rupees"
        followup = followup_message or "Which color and size would you like to select so I can add this to your bag?"

    lines = [
        intro,
        f"\n{header}",
        f"{label_name} {product.product_name}",
        f"{label_size} {sizes_str}",
        f"{label_color} {colors_str}",
        f"{label_price} {price_int} {currency}",
        f"\n{followup}"
    ]
    return "\n".join(lines)
