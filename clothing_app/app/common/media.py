"""Shared media URL resolution for product assets.

Keeps filesystem/path handling in one place so catalog and cart responses do not
implement competing image URL rules.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

LOCAL_IMAGE_ROUTE = "/assets/products/"


def resolve_product_image_url(image_url: str | None, product_images_dir: Path) -> str | None:
    """Resolve a stored product image value into a safe public URL.

    Absolute HTTP(S) URLs are preserved. Relative paths are exposed through the
    application's static product-assets route only when the target file exists.
    Path traversal and unsupported URL schemes are rejected.
    """
    if not image_url:
        return None
    raw = image_url.strip()
    if not raw:
        return None
    parsed = urlsplit(raw)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return raw
    if parsed.scheme or parsed.netloc:
        return None

    path = parsed.path.replace("\\", "/").lstrip("/")
    for prefix in ("assets/products/", "assets/", "products/"):
        if path.startswith(prefix):
            path = path.removeprefix(prefix)
            break

    parts = PurePosixPath(path).parts
    if not parts or any(part in {"", ".", ".."} for part in parts):
        return None

    root = product_images_dir.resolve()
    candidate = root.joinpath(*parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return f"{LOCAL_IMAGE_ROUTE}{'/'.join(parts)}"
