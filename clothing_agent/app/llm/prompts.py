"""Shared safety and response constraints for all agent prompts."""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    """Load a prompt from the prompts directory."""
    path = PROMPTS_DIR / f"{name}.txt"
    return path.read_text(encoding="utf-8").strip()


DOMAIN_POLICY = _load_prompt("domain_policy")
GROUNDING_POLICY = _load_prompt("grounding_policy")

SALES_PROMPT = f"{DOMAIN_POLICY}\n{_load_prompt('sales_prompt')}"
FASHION_PROMPT = f"{DOMAIN_POLICY}\n{_load_prompt('fashion_prompt')}\n{GROUNDING_POLICY}"
CART_EXTRACTION_PROMPT = _load_prompt("cart_extraction_prompt")
SEARCH_EXTRACTION_PROMPT = f"{DOMAIN_POLICY}\n{_load_prompt('search_extraction_prompt')}"
SHOPPING_RESPONSE_PROMPT = f"{DOMAIN_POLICY}\n{GROUNDING_POLICY}\n{_load_prompt('shopping_response_prompt')}"
ROUTER_PROMPT = _load_prompt("router_prompt")
CLARIFICATION_PROMPT = f"{DOMAIN_POLICY}\n{_load_prompt('clarification_prompt')}"

