"""Agent-facing tool contracts for semantic interactions with the backend."""

import logging
from app.clients.clothing_app.client import ClothingAppClient

from app.agent.tools.helpers import normalize_category_name, parse_categories_from_input
from app.agent.tools.catalog_tools import CatalogToolsMixin
from app.agent.tools.cart_tools import CartToolsMixin
from app.agent.tools.checkout_tools import CheckoutToolsMixin
from app.agent.tools.general_tools import GeneralToolsMixin

logger = logging.getLogger(__name__)


class AgentTools(
    CatalogToolsMixin,
    CartToolsMixin,
    CheckoutToolsMixin,
    GeneralToolsMixin
):
    """Agent tool layer providing semantic capabilities over the raw REST client."""

    def __init__(self, client: ClothingAppClient) -> None:
        self._client = client


__all__ = [
    "AgentTools",
    "normalize_category_name",
    "parse_categories_from_input",
    "CatalogToolsMixin",
    "CartToolsMixin",
    "CheckoutToolsMixin",
    "GeneralToolsMixin",
]
