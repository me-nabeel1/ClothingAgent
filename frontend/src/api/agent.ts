import { requestJson } from "./http";
import type { ChatResponse, ProductDetails, CartView } from "../types";

function normalizeBase(value: string | undefined, fallback: string) {
  return (value?.trim() || fallback).replace(/\/$/, "");
}

// In local development the root .env can still set full localhost URLs.
// In Docker/production, these relative defaults are proxied by Nginx so the
// browser uses one origin and does not need container hostnames or CORS.
export const AGENT_API_URL = normalizeBase(
  import.meta.env.VITE_AGENT_API_URL,
  "/agent",
);

export const CLOTHING_APP_URL = normalizeBase(
  import.meta.env.VITE_CLOTHING_APP_URL,
  "/catalog",
);

export function chat(message: string, session_id: string): Promise<ChatResponse> {
  return requestJson(`${AGENT_API_URL}/api/v1/chat`, {
    method: "POST",
    body: JSON.stringify({
      message,
      session_id,
    }),
  });
}

export async function getProductDetails(productId: number): Promise<ProductDetails> {
  return requestJson(`${CLOTHING_APP_URL}/api/v1/products/${productId}`);
}

export async function getCart(cartId: string): Promise<CartView> {
  return requestJson(`${CLOTHING_APP_URL}/api/v1/carts/${cartId}`);
}

export async function updateCartQuantity(cartId: string, itemId: string, quantity: number): Promise<CartView> {
  return requestJson(`${CLOTHING_APP_URL}/api/v1/carts/${cartId}/items/${itemId}`, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export async function removeCartItem(cartId: string, itemId: string): Promise<CartView> {
  return requestJson(`${CLOTHING_APP_URL}/api/v1/carts/${cartId}/items/${itemId}`, {
    method: "DELETE",
  });
}

export async function getHealth() {
  const [agent, ready] = await Promise.all([
    requestJson<{ status: string; llm_configured: boolean }>(`${AGENT_API_URL}/health`),
    requestJson<{ status: string; llm: string }>(`${AGENT_API_URL}/health/ready`),
  ]);
  return { agent, ready };
}

export async function getClothingAppHealth() {
  return requestJson<{ status: string }>(`${CLOTHING_APP_URL}/health/ready`);
}

export async function getMenu() {
  return requestJson<{ categories: { category_name: string; products: any[] }[] }>(`${CLOTHING_APP_URL}/api/v1/menu`);
}

export function resolveProductImage(imageUrl: string | null): string | null {
  if (!imageUrl) return null;
  const value = imageUrl.trim();
  if (!value) return null;
  if (/^https?:\/\//i.test(value)) return value;
  const normalized = value.startsWith("/") ? value : `/${value}`;
  return `${CLOTHING_APP_URL}${normalized}`;
}
