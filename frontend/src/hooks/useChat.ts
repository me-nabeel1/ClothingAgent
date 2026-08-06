import { useCallback, useEffect, useRef, useState } from "react";
import {
  getClothingAppHealth,
  getHealth,
  chat as postChat,
} from "../api/agent";
import { ApiError } from "../api/http";
import type {
  CartView,
  HealthStatus,
  TimelineMessage,
} from "../types";

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
  const [isStarting, setIsStarting] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthStatus>(INITIAL_HEALTH);
  const initializationRef = useRef(false);

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

  const createConversation = useCallback(async () => {
    setIsStarting(true);
    setError(null);
    setCart(null);
    try {
      const response = await postChat();
      setConversationId(response.conversation_id);
      setMessages([
        {
          id: response.message_id,
          role: "assistant",
          content: response.reply,
          createdAt: new Date().toISOString(),
          activeAgent: response.active_agent,
          intent: response.intent,
        },
      ]);
      setSuggestedActions(response.suggested_actions || []);
    } catch (reason) {
      const message = reason instanceof ApiError
        ? reason.message
        : "Could not connect to the clothing agent.";
      setError(message);
      setMessages([
        makeLocalMessage(
          "assistant",
          "I could not start the shopping conversation. Check that the clothing app and clothing agent are running.",
        ),
      ]);
    } finally {
      setIsStarting(false);
      void checkHealth();
    }
  }, [checkHealth]);

  useEffect(() => {
    if (initializationRef.current) return;
    initializationRef.current = true;
    void createConversation();
  }, [createConversation]);

  const sendMessage = useCallback(async (rawMessage: string) => {
    const message = rawMessage.trim();
    if (!message || !conversationId || isSending) return;

    setError(null);
    setMessages((current) => [...current, makeLocalMessage("user", message)]);
    setSuggestedActions([]);
    setIsSending(true);

    try {
      const response = await postChat(message, conversationId);
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
        },
      ]);
      if (response.cart) setCart(response.cart);
      setSuggestedActions(response.suggested_actions);
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
    isStarting,
    isSending,
    error,
    health,
    sendMessage,
    newConversation: createConversation,
    checkHealth,
  };
}
