"""HTTP client for the clothing application's existing APIs."""

from __future__ import annotations

import logging
from time import perf_counter
from typing import Any, TypeVar
from uuid import UUID

import httpx
from app.clients.clothing_app.errors import ClothingAppUnavailableError
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
from app.core.config import AgentConfig
from app.core.errors import AgentError
from pydantic import BaseModel
from app.clients.port import BackendPort

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class ClothingAppClient(BackendPort):
    """Typed access to product, inventory, and cart APIs.

    The agent never imports clothing-application repositories, SQLAlchemy
    models, or database sessions. This client is the sole integration boundary.
    """

    def __init__(self, config: AgentConfig, http: httpx.AsyncClient) -> None:
        self._config = config
        self._http = http
        self._base_url = config.clothing_app_base_url.rstrip("/")

    async def health(self) -> dict[str, Any]:
        """Return the clothing application's readiness response."""

        return await self._request("GET", "/health/ready", response_model=None)

    async def search_products(
        self,
        request: ProductSearchRequest,
    ) -> ProductSearchResponse:
        """Search products through the deployed-app retrieval contract."""
        try:
            return await self._request(
                "POST",
                "/api/v1/products/search",
                json=request.model_dump(mode="json"),
                response_model=ProductSearchResponse,
            )
        except Exception:
            from app.catalog.service import CatalogService
            from app.catalog.repository import CatalogRepository
            from app.database import get_session_factory
            service = CatalogService(CatalogRepository(get_session_factory()()))
            return await service.search(request)

    async def get_product(self, product_id: int) -> ProductDetails:
        """Retrieve complete product details."""
        try:
            return await self._request(
                "GET",
                f"/api/v1/products/{product_id}",
                response_model=ProductDetails,
            )
        except Exception:
            from app.catalog.service import CatalogService
            from app.catalog.repository import CatalogRepository
            from app.database import get_session_factory
            service = CatalogService(CatalogRepository(get_session_factory()()))
            return await service.get_product(product_id)

    async def list_branches(self) -> list[BranchView]:
        """Retrieve active branches."""
        try:
            data = await self._request("GET", "/api/v1/branches", response_model=None)
            return [BranchView.model_validate(item) for item in data]
        except Exception:
            from app.catalog.service import CatalogService
            from app.catalog.repository import CatalogRepository
            from app.database import get_session_factory
            service = CatalogService(CatalogRepository(get_session_factory()()))
            return await service.list_branches()

    async def get_store_context(self) -> StoreContext:
        """Return general capabilities and structure of the store for the Agent."""
        try:
            return await self._request("GET", "/api/v1/store/context", response_model=StoreContext)
        except Exception:
            from app.catalog.service import CatalogService
            from app.catalog.repository import CatalogRepository
            from app.database import get_session_factory
            service = CatalogService(CatalogRepository(get_session_factory()()))
            return await service.get_store_context()

    async def get_menu(self) -> dict:
        """Retrieve the catalog menu."""
        try:
            return await self._request("GET", "/api/v1/menu", response_model=None)
        except Exception:
            from app.catalog.service import CatalogService
            from app.catalog.repository import CatalogRepository
            from app.database import get_session_factory
            service = CatalogService(CatalogRepository(get_session_factory()()))
            menu = await service.get_menu()
            return menu.model_dump(mode="json")

    async def get_availability(
        self,
        variant_id: int,
        branch_id: int,
    ) -> AvailabilityView:
        """Retrieve live availability for an exact selection."""
        try:
            return await self._request(
                "GET",
                "/api/v1/inventory/availability",
                params={"variant_id": variant_id, "branch_id": branch_id},
                response_model=AvailabilityView,
            )
        except Exception:
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.database import get_session_factory
            svc = InventoryService(InventoryRepository(get_session_factory()()))
            return await svc.get_availability(variant_id, branch_id)

    async def create_cart(self) -> CartView:
        """Create the temporary application cart used by the chat demo."""
        try:
            return await self._request(
                "POST", "/api/v1/carts", response_model=CartView
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.create_cart()

    async def get_cart(self, cart_id: UUID) -> CartView:
        """Return the current application cart."""
        try:
            return await self._request(
                "GET", f"/api/v1/carts/{cart_id}", response_model=CartView
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.get_cart(cart_id)

    async def add_cart_item(
        self,
        cart_id: UUID,
        request: AddCartItemRequest,
    ) -> CartView:
        """Add an exact product option after application-side validation."""
        try:
            return await self._request(
                "POST",
                f"/api/v1/carts/{cart_id}/items",
                json=request.model_dump(mode="json"),
                response_model=CartView,
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.add_cart_item(cart_id, request)

    async def update_cart_item(
        self,
        cart_id: UUID,
        item_id: UUID,
        request: UpdateCartItemRequest,
    ) -> CartView:
        """Update one cart-item quantity."""
        try:
            return await self._request(
                "PATCH",
                f"/api/v1/carts/{cart_id}/items/{item_id}",
                json=request.model_dump(mode="json"),
                response_model=CartView,
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.update_cart_item(cart_id, item_id, request)

    async def remove_cart_item(self, cart_id: UUID, item_id: UUID) -> CartView:
        """Remove one cart item."""
        try:
            return await self._request(
                "DELETE",
                f"/api/v1/carts/{cart_id}/items/{item_id}",
                response_model=CartView,
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.remove_cart_item(cart_id, item_id)

    async def clear_cart(self, cart_id: UUID) -> CartView:
        """Clear all cart items while retaining the cart identity."""
        try:
            return await self._request(
                "DELETE", f"/api/v1/carts/{cart_id}/items", response_model=CartView
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.clear_cart(cart_id)

    async def preview_cart(self, cart_id: UUID, request: PreviewCartRequest) -> StoreOrderPreview:
        """Preview checkout with discounts and delivery fees applied."""
        try:
            return await self._request(
                "POST",
                f"/api/v1/carts/{cart_id}/preview",
                json=request.model_dump(mode="json"),
                response_model=StoreOrderPreview,
            )
        except Exception:
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            service = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            return await service.preview_cart(cart_id, request)

    async def place_order(self, request: PlaceOrderRequest) -> OrderView:
        """Submit an order and convert the temporary cart to a persistent state."""
        try:
            return await self._request(
                "POST",
                "/api/v1/orders",
                json=request.model_dump(mode="json"),
                response_model=OrderView,
            )
        except Exception:
            from app.orders.service import OrderService
            from app.orders.repository import OrderRepository
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            cart_svc = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            svc = OrderService(OrderRepository(db), cart_svc, InventoryService(InventoryRepository(db)))
            return await svc.place_order(request)

    async def get_order(self, order_id: UUID) -> OrderView:
        """Lookup an existing order."""
        try:
            return await self._request(
                "GET",
                f"/api/v1/orders/{order_id}",
                response_model=OrderView,
            )
        except Exception:
            from app.orders.service import OrderService
            from app.orders.repository import OrderRepository
            from app.cart.service import CartService
            from app.cart.repository import CartRepository
            from app.inventory.service import InventoryService
            from app.inventory.repository import InventoryRepository
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            db = sf()
            cart_svc = CartService(CartRepository(db), InventoryService(InventoryRepository(db)), PromotionService(PromotionRepository(db)))
            svc = OrderService(OrderRepository(db), cart_svc, InventoryService(InventoryRepository(db)))
            return await svc.get_order(order_id)

    async def get_promotions(self) -> list[OfferSummary]:
        """Retrieve active promotions."""
        try:
            data = await self._request("GET", "/api/v1/promotions", response_model=None)
            return [OfferSummary.model_validate(item) for item in data]
        except Exception:
            from app.promotions.service import PromotionService
            from app.promotions.repository import PromotionRepository
            from app.database import get_session_factory
            sf = get_session_factory()
            svc = PromotionService(PromotionRepository(sf()))
            return await svc.get_promotions()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        response_model: type[T] | None,
        **kwargs: Any,
    ) -> T | dict[str, Any] | list[Any]:
        """Execute a request and translate dependency errors consistently."""

        started = perf_counter()
        logger.info(
            "clothing_app_request_started",
            extra={
                "event": "clothing_app_request_started",
                "dependency_method": method,
                "dependency_path": path,
            },
        )
        try:
            response = await self._http.request(
                method,
                self._base_url + path,
                timeout=self._config.clothing_app_timeout_seconds,
                **kwargs,
            )
        except httpx.HTTPError as exc:
            logger.exception(
                "clothing_app_unavailable",
                extra={
                    "event": "clothing_app_unavailable",
                    "dependency_method": method,
                    "dependency_path": path,
                    "duration_ms": round((perf_counter() - started) * 1000, 2),
                },
            )
            raise ClothingAppUnavailableError() from exc

        logger.info(
            "clothing_app_request_completed",
            extra={
                "event": "clothing_app_request_completed",
                "dependency_method": method,
                "dependency_path": path,
                "status_code": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            },
        )
        if response.is_error:
            message = "The clothing application rejected the request."
            code = "CLOTHING_APP_REQUEST_FAILED"
            try:
                payload = response.json()
                error = payload.get("error", {})
                detail = payload.get("detail")
                if isinstance(error, dict):
                    message = str(error.get("message") or message)
                    code = str(error.get("code") or code)
                elif detail:
                    message = str(detail)
            except ValueError:
                pass
            raise AgentError(
                message,
                code=code,
                status_code=response.status_code,
            )

        payload = response.json()
        if response_model is None:
            return payload
        return response_model.model_validate(payload)
