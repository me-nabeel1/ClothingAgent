import {
  Menu,
  MessageCirclePlus,
  RefreshCw,
  ShoppingBag,
  Sparkles,
  WandSparkles,
  Mic,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { CartPanel } from "./components/CartPanel";
import { Composer } from "./components/Composer";
import { MessageBubble } from "./components/MessageBubble";
import { StatusDot } from "./components/StatusDot";
import { useChat } from "./hooks/useChat";
import "./styles.css";

const STARTER_PROMPTS = [
  "Hi",
  "I want to buy shirts",
  "I need black trousers in size 34 under PKR 5000",
  "What should I wear to an office dinner?",
];

export default function App() {
  const {
    messages,
    cart,
    suggestedActions,
    isStarting,
    isSending,
    error,
    health,
    sendMessage,
    newConversation,
    checkHealth,
  } = useChat();
  const [cartOpen, setCartOpen] = useState(false);
  const [isAudioMode, setIsAudioMode] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isSending]);

  useEffect(() => {
    if (cart && cart.total_quantity > 0) setCartOpen(true);
  }, [cart?.total_quantity]);

  const disabled = isStarting || isSending;
  const appName = import.meta.env.VITE_APP_NAME ?? "Atelier AI";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand__mark"><WandSparkles size={22} /></div>
          <div>
            <strong>{appName}</strong>
            <span>Personal shopping concierge</span>
          </div>
        </div>

        <div className="topbar__status"></div>

        <div className="topbar__actions">
          <button 
            className={`icon-button ${isAudioMode ? 'button--audio active' : ''}`} 
            type="button" 
            title="Toggle Audio Mode"
            onClick={() => setIsAudioMode(!isAudioMode)}
          >
            <Mic size={18} />
          </button>
          <button className="button button--outline" type="button" disabled={disabled} onClick={() => void newConversation()}>
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
          <div className="chat-panel__intro">
            <div></div>
            <button className="mobile-cart-toggle" type="button" onClick={() => setCartOpen(true)} aria-label="Open cart">
              <Menu size={19} />
            </button>
          </div>

          <div className="messages" ref={scrollRef}>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                disabled={disabled}
                onAction={(value) => void sendMessage(value)}
              />
            ))}

            {isSending && (
              <div className="message-row message-row--assistant">
                <div className="message-avatar"><Sparkles size={17} /></div>
                <div className="typing-indicator" aria-label="Assistant is typing">
                  <span /><span /><span />
                </div>
              </div>
            )}
          </div>

          <div className="chat-controls">
            {error && <div className="error-banner">{error}</div>}

            <div className="suggestion-strip" aria-label="Suggested prompts">
              {(suggestedActions.length > 0 ? suggestedActions : STARTER_PROMPTS).slice(0, 4).map((action) => (
                <button key={action} type="button" disabled={disabled} onClick={() => void sendMessage(action)}>
                  {action}
                </button>
              ))}
            </div>

            <Composer 
              disabled={disabled} 
              isAudioMode={isAudioMode} 
              onExitAudio={() => setIsAudioMode(false)}
              onSend={(value) => void sendMessage(value)} 
            />
          </div>
        </section>

        <CartPanel
          cart={cart}
          open={cartOpen}
          disabled={disabled}
          onClose={() => setCartOpen(false)}
          onAction={(value) => void sendMessage(value)}
        />
        {cartOpen && <button className="cart-backdrop" type="button" aria-label="Close cart" onClick={() => setCartOpen(false)} />}
      </main>
    </div>
  );
}
