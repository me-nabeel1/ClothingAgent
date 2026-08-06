import { requestJson } from "./http";
import type {
  ChatTurnResponse,
} from "../types";

export const AGENT_API_URL = (
  import.meta.env.VITE_AGENT_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export const CLOTHING_APP_URL = (
  import.meta.env.VITE_CLOTHING_APP_URL ?? "http://127.0.0.1:8100"
).replace(/\/$/, "");

export function chat(message?: string, conversation_id?: string | null): Promise<ChatTurnResponse> {
  return requestJson(`${AGENT_API_URL}/api/v1/chat`, {
    method: "POST",
    body: JSON.stringify({ 
      message: message || null, 
      conversation_id: conversation_id || null 
    }),
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

export function resolveProductImage(imageUrl: string | null): string | null {
  if (!imageUrl) return null;
  if (/^https?:\/\//i.test(imageUrl)) return imageUrl;
  const normalized = imageUrl.startsWith("/") ? imageUrl : `/${imageUrl}`;
  return `${CLOTHING_APP_URL}${normalized}`;
}
