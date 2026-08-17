from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.clients.clothing_app.schemas import (
    AddCartItemRequest,
    AvailabilityView,
    BranchView,
    CartView,
    ProductDetails,
    ProductSearchRequest,
    ProductSearchResponse,
    StoreContext,
    UpdateCartItemRequest,
    PreviewCartRequest,
    StoreOrderPreview,
    PlaceOrderRequest,
    OrderView,
    OfferSummary,
)

class BackendPort(ABC):
    """Every method a backend integration must provide for the agent to function. To integrate a new backend,
    implement this class, normalizing that backend's responses into these same
    Pydantic models. Nothing in app/agent/ should ever import a concrete backend
    client directly — only this contract."""

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        pass

    @abstractmethod
    async def get_store_context(self) -> StoreContext:
        pass

    @abstractmethod
    async def search_products(
        self,
        request: ProductSearchRequest,
    ) -> ProductSearchResponse:
        pass

    @abstractmethod
    async def get_product(self, product_id: int) -> ProductDetails:
        pass

    @abstractmethod
    async def list_branches(self) -> list[BranchView]:
        pass

    @abstractmethod
    async def get_menu(self) -> dict:
        pass

    @abstractmethod
    async def get_availability(
        self,
        variant_id: int,
        branch_id: int,
    ) -> AvailabilityView:
        pass

    @abstractmethod
    async def create_cart(self) -> CartView:
        pass

    @abstractmethod
    async def get_cart(self, cart_id: UUID) -> CartView:
        pass

    @abstractmethod
    async def add_cart_item(
        self,
        cart_id: UUID,
        request: AddCartItemRequest,
    ) -> CartView:
        pass

    @abstractmethod
    async def update_cart_item(
        self,
        cart_id: UUID,
        item_id: UUID,
        request: UpdateCartItemRequest,
    ) -> CartView:
        pass

    @abstractmethod
    async def remove_cart_item(self, cart_id: UUID, item_id: UUID) -> CartView:
        pass

    @abstractmethod
    async def clear_cart(self, cart_id: UUID) -> CartView:
        pass

    @abstractmethod
    async def preview_cart(self, cart_id: UUID, request: PreviewCartRequest) -> StoreOrderPreview:
        pass

    @abstractmethod
    async def place_order(self, request: PlaceOrderRequest) -> OrderView:
        pass

    async def get_order(self, order_id: UUID) -> OrderView:
        raise NotImplementedError("get_order — implemented in Phase 2")

    @abstractmethod
    async def get_promotions(self) -> list[OfferSummary]:
        pass
