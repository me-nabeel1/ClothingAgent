from decimal import Decimal
from pathlib import Path

import pytest

from app.catalog.schemas import ProductSearchRequest
from app.catalog.service import CatalogService

FIXTURE_IMAGES_DIR = Path(__file__).parent / "fixtures" / "product_images"


def product_row(image_url: str | None) -> dict[str, object]:
    return {
        "product_id": 1,
        "variant_id": 10,
        "branch_id": 100,
        "article_code": "TEE-001",
        "product_name": "Flex Compression Tee",
        "category": "T-shirts",
        "gender": "Men",
        "brand": "Demo",
        "color": "Black",
        "size": "M",
        "price": Decimal("29.99"),
        "branch_code": "MAIN",
        "branch_name": "Main",
        "city": "Lahore",
        "available_quantity": 3,
        "in_transit_quantity": 0,
        "image_url": image_url,
        "material": "Cotton",
        "fit": "Slim",
        "season": "Summer",
        "description": "Training tee",
    }


class FakeCatalogRepository:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self._rows = rows

    async def search_rows(self, *_args, **_kwargs) -> list[dict[str, object]]:
        return self._rows


@pytest.mark.asyncio
async def test_search_omits_missing_local_product_images() -> None:
    service = CatalogService(
        FakeCatalogRepository([product_row("/assets/missing-tee.svg")]),
        product_images_dir=FIXTURE_IMAGES_DIR,
    )

    response = await service.search(ProductSearchRequest(limit=1))

    assert response.products[0].image_url is None


@pytest.mark.asyncio
async def test_search_normalizes_existing_legacy_product_image_paths() -> None:
    service = CatalogService(
        FakeCatalogRepository([product_row("/assets/flex-compression-tee.svg")]),
        product_images_dir=FIXTURE_IMAGES_DIR,
    )

    response = await service.search(ProductSearchRequest(limit=1))

    assert response.products[0].image_url == "/assets/products/flex-compression-tee.svg"
