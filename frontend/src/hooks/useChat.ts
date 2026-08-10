import { useCallback, useEffect, useRef, useState } from "react";
import {
  getClothingAppHealth,
  getHealth,
  chat as postChat,
} from "../api/agent";
import { ApiError } from "../api/http";
import type { CartView, HealthStatus, TimelineMessage } from "../types";

const INITIAL_HEALTH: HealthStatus = {
  agent: "checking",
  clothingApp: "checking",
  llm: "unknown",
};

function makeLocalMessage(role: "user" | "assistant", content: string): TimelineMessage {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function useChat() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<TimelineMessage[]>([]);
  const [cart, setCart] = useState<CartView | null>(null);
  const [suggestedActions, setSuggestedActions] = useState<string[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus>(INITIAL_HEALTH);
  const healthStarted = useRef(false);

  const checkHealth = useCallback(async () => {
    const next: HealthStatus = {
      agent: "offline",
      clothingApp: "offline",
      llm: "unknown",
    };
    try {
      const result = await getHealth();
      next.agent = result.agent.status === "ok" ? "online" : "offline";
      next.clothingApp = result.ready.status === "ready" ? "online" : "offline";
      next.llm = result.ready.llm === "configured" ? "configured" : "local_fallback";
    } catch {
      try {
        const app = await getClothingAppHealth();
        next.clothingApp = app.status === "ready" ? "online" : "offline";
      } catch {
        next.clothingApp = "offline";
      }
    }
    setHealth(next);
  }, []);

  useEffect(() => {
    if (healthStarted.current) return;
    healthStarted.current = true;
    void checkHealth();
  }, [checkHealth]);

  const newConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setCart(null);
    setSuggestedActions([]);
    setError(null);
  }, []);

  const sendMessage = useCallback(async (rawMessage: string) => {
    const message = rawMessage.trim();
    if (!message || isSending) return;

    setError(null);
    setMessages((current) => [...current, makeLocalMessage("user", message)]);
    setSuggestedActions([]);
    setIsSending(true);

    try {
      const response = await postChat(message, conversationId);
      if (!conversationId) setConversationId(response.conversation_id);
      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: "assistant",
          content: response.reply,
          createdAt: new Date().toISOString(),
          products: response.products,
          suggestedActions: response.suggested_actions,
          activeAgent: response.active_agent,
          intent: response.intent,
          uiActions: response.ui_actions || [],
        },
      ]);
      if (response.cart) setCart(response.cart);
      setSuggestedActions(response.suggested_actions || []);
    } catch (reason) {
      const messageText = reason instanceof ApiError
        ? reason.message
        : "The request failed. Please try again.";
      setError(messageText);
      setMessages((current) => [
        ...current,
        makeLocalMessage("assistant", `I hit a connection problem: ${messageText}`),
      ]);
      void checkHealth();
    } finally {
      setIsSending(false);
    }
  }, [checkHealth, conversationId, isSending]);

  return {
    conversationId,
    messages,
    cart,
    suggestedActions,
    isStarting: false,
    isSending,
    error,
    health,
    sendMessage,
    newConversation,
    checkHealth,
  };
}
