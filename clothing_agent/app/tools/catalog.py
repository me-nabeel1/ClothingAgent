"""Catalog and inventory tools."""

from decimal import Decimal
from typing import Annotated

from app.clients.clothing_app.schemas import ProductSearchRequest
from langchain_core.tools import tool

from app.core.container import get_container

@tool
async def search_products(
    query: Annotated[str | None, "Natural language search query for the products."] = None,
    category: Annotated[str | None, "The category to filter by (e.g. 'Shirts', 'Pants')."] = None,
    color: Annotated[str | None, "The color to filter by."] = None,
    size: Annotated[str | None, "The size to filter by (e.g. 'S', 'M', 'L')."] = None,
    min_price: Annotated[float | None, "Minimum price."] = None,
    max_price: Annotated[float | None, "Maximum price."] = None,
    limit: Annotated[int, "Maximum number of results to return (default 5)"] = 5,
) -> dict:
    """
    Search the connected store catalog for products matching the customer's requirements.
    Use this tool whenever product facts, availability-related catalog information, 
    price, category, or attributes are needed. Never invent catalog information.
    """
    container = get_container()
    client = container.clothing_app_client
    
    req = ProductSearchRequest(
        query=query,
        category=category,
        color=color,
        size=size,
        min_price=Decimal(min_price) if min_price else None,
        max_price=Decimal(max_price) if max_price else None,
        limit=limit,
    )
    
    try:
        response = await client.search_products(req)
        return response.model_dump(mode="json")
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_product_details(
    product_id: Annotated[int, "The exact ID of the product to look up."]
) -> dict:
    """
    Retrieve authoritative and complete product information, including its variants, 
    sizes, colors, and prices. Call this when you need detailed options for a specific product.
    """
    container = get_container()
    client = container.clothing_app_client
    
    try:
        response = await client.get_product(product_id)
        return response.model_dump(mode="json")
    except Exception as e:
        return {"error": str(e)}


@tool
async def check_availability(
    variant_id: Annotated[int, "The exact variant ID of the selected color/size combination."],
    branch_id: Annotated[int, "The branch ID to check availability in."]
) -> dict:
    """
    Check whether a specific variant is actually in stock at a specific branch.
    Never infer stock from a previous search result when a final availability check is requested.
    """
    container = get_container()
    client = container.clothing_app_client
    
    try:
        response = await client.get_availability(variant_id=variant_id, branch_id=branch_id)
        return response.model_dump(mode="json")
    except Exception as e:
        return {"error": str(e)}
