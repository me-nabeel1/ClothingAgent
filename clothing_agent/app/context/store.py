"""Manager for caching and providing dynamic store capabilities and vocabulary."""

import logging
from typing import Optional
from ..clients.clothing_app.client import ClothingAppClient
from ..clients.clothing_app.schemas import StoreContext

logger = logging.getLogger(__name__)

class StoreContextManager:
    """Manages the dynamic vocabulary of the connected application."""

    def __init__(self, client: ClothingAppClient) -> None:
        self._client = client
        self._context: Optional[StoreContext] = None

    @property
    def is_loaded(self) -> bool:
        """Return True if the context has been successfully loaded."""
        return self._context is not None

    def get_context(self) -> StoreContext:
        """Return the loaded context.
        
        Raises:
            RuntimeError: If context has not been loaded yet.
        """
        if not self._context:
            raise RuntimeError("Store context has not been loaded. Call load_context() first.")
        return self._context

    async def load_context(self) -> StoreContext:
        """Load the store context from the application API.
        
        This retrieves all available branches, categories, product types, occasions,
        colors, sizes, etc., directly from the source of truth.
        """
        logger.info("loading_store_context", extra={"event": "loading_store_context"})
        self._context = await self._client.get_store_context()
        logger.info(
            "store_context_loaded",
            extra={
                "event": "store_context_loaded",
                "categories": len(self._context.categories),
                "branches": len(self._context.branches),
            },
        )
        return self._context

    async def refresh_context(self) -> StoreContext:
        """Force a refresh of the context."""
        return await self.load_context()
