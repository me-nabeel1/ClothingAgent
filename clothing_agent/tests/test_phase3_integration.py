"""Tests for Phase 3 semantic-to-HTTP integration adapters."""

from __future__ import annotations

from uuid import uuid4

import httpx
import pytest

from clothing_agent.app.agent.contracts import ToolName
from clothing_agent.app.integration.client import CommerceAPIClient, CommerceToolAdapter
from clothing_agent.app.integration.http import AsyncJSONTransport
from clothing_agent.app.integration.schemas import ProductSearchRequest


@pytest.fixture
def mock_transport():
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST" and request.url.path == "/api/v1/products/search":
            payload = request.read().decode()
            assert '"sizes":["L"]' in payload
            return httpx.Response(
                200,
                json={
                    "products": [
                        {
                            "product_id": 1,
                            "variant_id": 10,
                            "branch_id": 3,
                            "article_code": "NS-SH-001",
                            "product_name": "Oxford Shirt",
                            "category": "shirts",
                            "color": "Black",
                            "size": "L",
                            "price": "4000.00",
                            "branch_code": "ISB-F7",
                            "branch_name": "Northstar F-7",
                            "city": "Islamabad",
                            "available_quantity": 3,
                        }
                    ],
                    "result_count": 1,
                },
            )
        if request.method == "GET" and request.url.path == "/api/v1/branches":
            return httpx.Response(
                200,
                json=[
                    {
                        "branch_id": 3,
                        "branch_code": "ISB-F7",
                        "branch_name": "Northstar F-7",
                        "city": "Islamabad",
                        "address": "F-7, Islamabad",
                    }
                ],
            )
        if request.method == "GET" and request.url.path == "/api/v1/inventory/availability":
            return httpx.Response(
                200,
                json={
                    "product_id": 1,
                    "variant_id": 10,
                    "branch_id": 3,
                    "branch_code": "ISB-F7",
                    "branch_name": "Northstar F-7",
                    "color": "Black",
                    "size": "L",
                    "price": "4000.00",
                    "available_quantity": 3,
                    "in_transit_quantity": 0,
                    "is_available": True,
                },
            )
        if request.method == "POST" and request.url.path == "/api/v1/carts":
            return httpx.Response(200, json={"cart_id": str(uuid4()), "item_count": 0, "subtotal": "0.00"})
        if request.method == "POST" and request.url.path.endswith("/items"):
            return httpx.Response(200, json={"cart_id": str(uuid4()), "item_count": 1, "subtotal": "4000.00"})
        if request.method == "POST" and request.url.path.endswith("/preview"):
            return httpx.Response(
                200,
                json={
                    "cart_id": request.url.path.split("/")[4],
                    "subtotal": "4000.00",
                    "discount_total": "0.00",
                    "delivery_fee": "200.00",
                    "grand_total": "4200.00",
                    "applied_offers": [],
                },
            )
        if request.method == "POST" and request.url.path == "/api/v1/orders":
            return httpx.Response(200, json={"order_number": "NS-000001", "status": "PLACED", "grand_total": "4200.00"})
        return httpx.Response(404, json={"detail": "not found"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    transport = AsyncJSONTransport("http://commerce.test", client=client)
    return transport, client


@pytest.mark.asyncio
async def test_product_search_maps_semantic_request_to_existing_api(mock_transport) -> None:
    transport, client = mock_transport
    commerce = CommerceAPIClient(transport, {})
    request = ProductSearchRequest(categories=["shirts"], size_mapping={"shirts": "L"}, colors=["black"])

    response = await commerce.get_products(request)

    assert response.result_count == 1
    assert response.products[0].product_name == "Oxford Shirt"
    await client.aclose()


@pytest.mark.asyncio
async def test_branch_and_availability_use_existing_endpoints(mock_transport) -> None:
    transport, client = mock_transport
    commerce = CommerceAPIClient(transport, {})

    branches = await commerce.get_branches()
    availability = await commerce.check_availability(variant_id=10, branch_id=3)

    assert branches[0].branch_code == "ISB-F7"
    assert availability.is_available is True
    assert availability.available_quantity == 3
    await client.aclose()


@pytest.mark.asyncio
async def test_cart_checkout_and_order_use_existing_endpoints(mock_transport) -> None:
    transport, client = mock_transport
    commerce = CommerceAPIClient(transport, {})

    cart = await commerce.create_cart(session_id=uuid4())
    assert cart.cart_id is not None

    updated = await commerce.add_to_cart(
        cart_id=cart.cart_id,
        variant_id=10,
        branch_id=3,
        quantity=1,
    )
    assert updated.item_count == 1

    preview = await commerce.preview_checkout(cart_id=cart.cart_id)
    assert preview.grand_total == 4200

    order = await commerce.place_order(
        {
            "cart_id": str(cart.cart_id),
            "customer_name": "Ahmed",
            "phone": "03000000000",
            "delivery_address": "DHA",
            "city": "Lahore",
            "explicit_confirmation": True,
        }
    )
    assert order.order_number == "NS-000001"
    await client.aclose()


@pytest.mark.asyncio
async def test_tool_adapter_dispatches_semantic_tool() -> None:
    async def fake_transport(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "products": [],
                "result_count": 0,
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(fake_transport))
    commerce = CommerceAPIClient(AsyncJSONTransport("http://commerce.test", client=client), {})
    adapter = CommerceToolAdapter(commerce)

    result = await adapter.execute(
        ToolName.GET_PRODUCTS,
        {"categories": ["shirts"], "limit": 4},
    )

    assert result.result_count == 0
    await client.aclose()
