import {
  MessageCirclePlus,
  ShoppingBag,
  Sparkles,
  WandSparkles,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { CartPanel } from "./components/CartPanel";
import { Composer } from "./components/Composer";
import { MessageBubble } from "./components/MessageBubble";
import { useChat } from "./hooks/useChat";
import "./styles.css";

const STARTER_PROMPTS = [
  "I want a casual shirt for summer",
  "Show me black trousers under PKR 5,000",
  "I need something for the gym",
];

export default function App() {
  const {
    messages,
    cart,
    suggestedActions,
    isSending,
    error,
    health,
    sendMessage,
    newConversation,
  } = useChat();

  const [cartOpen, setCartOpen] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isSending]);

  const appName = import.meta.env.VITE_APP_NAME ?? "Atelier AI";
  const available = health.agent === "online" && health.clothingApp === "online";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand__mark"><WandSparkles size={20} /></div>
          <div>
            <strong>{appName}</strong>
            <span>AI shopping concierge</span>
          </div>
        </div>

        <div className="topbar__actions">
          <div className={`status-pill ${available ? "status-pill--online" : ""}`}>
            <i /> {available ? "Concierge online" : "Connecting"}
          </div>
          <button
            className="button button--outline new-chat-button"
            type="button"
            disabled={isSending}
            onClick={newConversation}
          >
            <MessageCirclePlus size={16} /> New chat
          </button>
          <button className="cart-button" type="button" onClick={() => setCartOpen(true)}>
            <ShoppingBag size={18} />
            <span>Bag</span>
            <b>{cart?.total_quantity ?? 0}</b>
          </button>
        </div>
      </header>

      <main className="workspace">
        <section className="chat-panel">
          <div className="messages" ref={scrollRef}>
            {messages.length === 0 ? (
              <div className="empty-state">
                <div className="empty-state__icon"><Sparkles size={24} /></div>
                <span className="section-kicker">Personal shopping, without the scrolling</span>
                <h1>What are you shopping for today?</h1>
                <p>
                  Tell me the item, occasion, color, size, or budget. I’ll narrow it down and show a few strong options.
                </p>
                <div className="starter-grid">
                  {STARTER_PROMPTS.map((prompt) => (
                    <button key={prompt} disabled={isSending} onClick={() => void sendMessage(prompt)}>
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  disabled={isSending}
                  onAction={(value) => void sendMessage(value)}
                />
              ))
            )}

            {isSending && (
              <div className="message-row message-row--assistant">
                <div className="message-avatar"><Sparkles size={17} /></div>
                <div className="typing-indicator" aria-label="Assistant is thinking">
                  <span /><span /><span />
                </div>
              </div>
            )}
          </div>

          <div className="chat-controls">
            {error && <div className="error-banner">{error}</div>}
            {messages.length > 0 && suggestedActions.length > 0 && (
              <div className="suggestion-strip" aria-label="Suggested next actions">
                {suggestedActions.slice(0, 3).map((action) => (
                  <button key={action} type="button" disabled={isSending} onClick={() => void sendMessage(action)}>
                    {action}
                  </button>
                ))}
              </div>
            )}
            <Composer disabled={isSending} onSend={(value) => void sendMessage(value)} />
          </div>
        </section>

        <CartPanel
          cart={cart}
          open={cartOpen}
          disabled={isSending}
          onClose={() => setCartOpen(false)}
          onAction={(value) => void sendMessage(value)}
        />
        {cartOpen && (
          <button
            className="cart-backdrop"
            type="button"
            aria-label="Close cart"
            onClick={() => setCartOpen(false)}
          />
        )}
      </main>
    </div>
  );
}
