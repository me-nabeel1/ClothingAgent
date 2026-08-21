"""Optional V2-ready provider boundaries for identity and payments.

V1 remains payment-free and session-based. These protocols make the eventual
integration points explicit without coupling the order domain to Stripe, a
specific auth server, or another vendor.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from decimal import Decimal


@dataclass(frozen=True)
class CustomerIdentity:
    """Normalized customer identity supplied by an authentication adapter."""
    customer_id: str | None = None
    display_name: str | None = None
    phone: str | None = None


class CustomerIdentityProvider(Protocol):
    """Future authentication boundary for a real store integration."""
    async def resolve(self, token: str) -> CustomerIdentity: ...


@dataclass(frozen=True)
class PaymentIntent:
    """Normalized payment intent used by an eventual payment provider."""
    payment_id: str
    amount: Decimal
    currency: str
    status: str


class PaymentProvider(Protocol):
    """Future payment gateway boundary; V1 does not call it."""
    async def create_payment(self, *, amount: Decimal, currency: str, reference: str) -> PaymentIntent: ...
    async def get_payment(self, payment_id: str) -> PaymentIntent: ...
