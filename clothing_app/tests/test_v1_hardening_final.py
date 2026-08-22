"""Unit tests for cart mutation, checkout confirmation invalidation, idempotency, and reservation invariants."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
from types import SimpleNamespace

import pytest
from app.cart.schemas import AddCartItemRequest, PreviewCartRequest
from app.cart.service import CartService
from app.orders.schemas import PlaceOrderRequest
from app.orders.service import OrderService
from app.inventory.reservations import ReservationService
from app.common.exceptions import ConflictError


class MockInventoryService:
    def __init__(self, stock: int = 10, unit_price: Decimal = Decimal("2500.00")):
        self.stock = stock
        self.unit_price = unit_price

    async def variant_snapshot(self, variant_id: int, branch_id: int):
        return SimpleNamespace(
            product_id=1,
            variant_id=variant_id,
            branch_id=branch_id,
            article_code="NS-TEST-001",
            product_name="Test Product",
            category_id=1,
            color="Black",
            size="M",
            unit_price=self.unit_price,
            image_url=None,
        )


class MockPromotionService:
    async def evaluate_cart(self, subtotal, items, offer_code):
        return SimpleNamespace(
            free_delivery=False,
            discount_total=Decimal("0.00"),
            applied_offers=[],
        )


class MockReservationService:
    def __init__(self):
        self.reserved_calls = []

    async def release_expired(self):
        pass

    async def reserve(self, cart_id, variant_id, branch_id, quantity, expires_at):
        self.reserved_calls.append((cart_id, variant_id, branch_id, quantity))

    async def release_for_item(self, cart_id, variant_id, branch_id):
        pass

    async def release_for_cart(self, cart_id):
        pass


class MockCartRepository:
    def __init__(self):
        self.cart = SimpleNamespace(
            cart_id=uuid4(),
            session_id="test-session",
            store_id="northstar",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
            confirmation_token=None,
            items=[],
        )

    async def require(self, cart_id, for_update=False):
        return self.cart

    async def add_or_increment(self, cart_id, product_id, variant_id, branch_id, quantity):
        item_id = uuid4()
        existing = next((i for i in self.cart.items if i.variant_id == variant_id and i.branch_id == branch_id), None)
        if existing:
            existing.quantity += quantity
        else:
            item = SimpleNamespace(
                item_id=item_id,
                cart_id=cart_id,
                product_id=product_id,
                variant_id=variant_id,
                branch_id=branch_id,
                quantity=quantity,
                added_at=datetime.now(timezone.utc),
            )
            self.cart.items.append(item)
        return self.cart

    async def update_quantity(self, cart_id, item_id, quantity):
        if quantity <= 0:
            self.cart.items = [i for i in self.cart.items if i.item_id != item_id]
        else:
            item = next((i for i in self.cart.items if i.item_id == item_id), None)
            if item:
                item.quantity = quantity
        return self.cart

    async def remove_item(self, cart_id, item_id):
        self.cart.items = [i for i in self.cart.items if i.item_id != item_id]
        return self.cart

    async def clear(self, cart_id):
        self.cart.items = []
        return self.cart


@pytest.mark.asyncio
async def test_remove_cart_item() -> None:
    repo = MockCartRepository()
    inv = MockInventoryService()
    promos = MockPromotionService()
    res = MockReservationService()
    config = SimpleNamespace(store_id="northstar", cart_ttl_hours=24, product_images_dir="tools/data/product_images")

    service = CartService(repo, inv, promos, config, res)
    cart_view = await service.add(repo.cart.cart_id, AddCartItemRequest(variant_id=1, branch_id=1, quantity=2))
    assert cart_view.total_quantity == 2

    item_id = cart_view.items[0].item_id
    updated_view = await service.remove(repo.cart.cart_id, item_id)
    assert updated_view.total_quantity == 0
    assert len(updated_view.items) == 0


@pytest.mark.asyncio
async def test_quantity_propagation() -> None:
    repo = MockCartRepository()
    inv = MockInventoryService(unit_price=Decimal("3000.00"))
    promos = MockPromotionService()
    res = MockReservationService()
    config = SimpleNamespace(store_id="northstar", cart_ttl_hours=24, product_images_dir="tools/data/product_images")

    service = CartService(repo, inv, promos, config, res)
    cart_view = await service.add(repo.cart.cart_id, AddCartItemRequest(variant_id=1, branch_id=1, quantity=1))
    assert cart_view.subtotal == Decimal("3000.00")

    item_id = cart_view.items[0].item_id
    updated_view = await service.update(repo.cart.cart_id, item_id, 3)
    assert updated_view.total_quantity == 3
    assert updated_view.subtotal == Decimal("9000.00")
    assert updated_view.items[0].line_total == Decimal("9000.00")


@pytest.mark.asyncio
async def test_confirmation_invalidation_on_cart_mutation() -> None:
    repo = MockCartRepository()
    inv = MockInventoryService()
    promos = MockPromotionService()
    res = MockReservationService()
    config = SimpleNamespace(store_id="northstar", cart_ttl_hours=24, product_images_dir="tools/data/product_images")

    service = CartService(repo, inv, promos, config, res)
    await service.add(repo.cart.cart_id, AddCartItemRequest(variant_id=1, branch_id=1, quantity=1))

    preview = await service.preview(repo.cart.cart_id, PreviewCartRequest())
    assert preview.confirmation_token is not None
    assert repo.cart.confirmation_token == preview.confirmation_token

    # Mutate cart by adding another item -> must invalidate confirmation token
    await service.add(repo.cart.cart_id, AddCartItemRequest(variant_id=2, branch_id=1, quantity=1))
    assert repo.cart.confirmation_token is None


@pytest.mark.asyncio
async def test_order_placement_requires_valid_confirmation() -> None:
    repo = MockCartRepository()
    inv = MockInventoryService()
    promos = MockPromotionService()
    res = MockReservationService()
    config = SimpleNamespace(store_id="northstar", cart_ttl_hours=24, product_images_dir="tools/data/product_images")

    cart_service = CartService(repo, inv, promos, config, res)
    async def mock_get(req_id):
        return None

    async def mock_create(cart, preview, req):
        return SimpleNamespace(
            order_id=uuid4(), order_number="NS-0001", status="PLACED", subtotal=preview.subtotal,
            discount_total=preview.discount_total, delivery_fee=preview.delivery_fee, grand_total=preview.grand_total,
            applied_offer_code=None, customer_name=req.customer_name, phone=req.phone,
            delivery_address=req.delivery_address, city=req.city, delivery_notes=req.delivery_notes,
            created_at=datetime.now(timezone.utc), items=[]
        )

    order_repo = SimpleNamespace(
        get_by_checkout_request_id=mock_get,
        create_order_from_cart=mock_create,
    )
    order_service = OrderService(order_repo, repo, cart_service)

    await cart_service.add(repo.cart.cart_id, AddCartItemRequest(variant_id=1, branch_id=1, quantity=1))
    req = PlaceOrderRequest(
        cart_id=repo.cart.cart_id,
        checkout_request_id="REQ-12345678",
        customer_name="Ali Khan",
        phone="03001234567",
        delivery_address="F-7",
        city="Islamabad",
    )

    # Placed without preview -> must fail with CONFIRMATION_INVALID
    with pytest.raises(ConflictError) as exc_info:
        await order_service.place_order(req)
    assert exc_info.value.code == "CONFIRMATION_INVALID"

    # Preview cart -> confirmation generated -> order succeeds
    await cart_service.preview(repo.cart.cart_id, PreviewCartRequest())
    order_view = await order_service.place_order(req)
    assert order_view.order_number == "NS-0001"


@pytest.mark.asyncio
async def test_checkout_idempotency() -> None:
    repo = MockCartRepository()
    inv = MockInventoryService()
    promos = MockPromotionService()
    res = MockReservationService()
    config = SimpleNamespace(store_id="northstar", cart_ttl_hours=24, product_images_dir="tools/data/product_images")

    cart_service = CartService(repo, inv, promos, config, res)
    placed_order = SimpleNamespace(
        order_id=uuid4(), order_number="NS-0001", status="PLACED", subtotal=Decimal("2500.00"),
        discount_total=Decimal("0.00"), delivery_fee=Decimal("15.00"), grand_total=Decimal("2515.00"),
        applied_offer_code=None, customer_name="Ali Khan", phone="03001234567",
        delivery_address="F-7", city="Islamabad", delivery_notes=None,
        created_at=datetime.now(timezone.utc), items=[]
    )

    async def mock_get(req_id):
        if req_id == "REQ-12345678":
            return placed_order
        return None

    order_repo = SimpleNamespace(
        get_by_checkout_request_id=mock_get,
        create_order_from_cart=None,
    )
    order_service = OrderService(order_repo, repo, cart_service)

    req = PlaceOrderRequest(
        cart_id=repo.cart.cart_id,
        checkout_request_id="REQ-12345678",
        customer_name="Ali Khan",
        phone="03001234567",
        delivery_address="F-7",
        city="Islamabad",
    )

    res1 = await order_service.place_order(req)
    assert res1.order_number == "NS-0001"

