import { Bot, Sparkles, UserRound } from "lucide-react";
import type { TimelineMessage } from "../types";
import { ProductCard } from "./ProductCard";

interface MessageBubbleProps {
  message: TimelineMessage;
  disabled: boolean;
  onAction: (message: string) => void;
}

function formatTime(value: string) {
  return new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function MessageBubble({ message, disabled, onAction }: MessageBubbleProps) {
  const assistant = message.role === "assistant";
  return (
    <div className={`message-row ${assistant ? "message-row--assistant" : "message-row--user"}`}>
      <div className="message-avatar" aria-hidden="true">
        {assistant ? <Bot size={17} /> : <UserRound size={17} />}
      </div>
      <div className="message-content">
        <div className="message-bubble">
          <p>{message.content}</p>
          <span className="message-time">{formatTime(message.createdAt)}</span>
        </div>


        {message.products && message.products.length > 0 && (
          <div className="product-grid">
            {message.products.map((product, index) => (
              <ProductCard
                key={`${product.variant_id}-${product.branch_id}-${index}`}
                product={product}
                position={index + 1}
                disabled={disabled}
                onAction={onAction}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
