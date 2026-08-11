import { Minus, Plus, ShoppingBag, Trash2, X } from "lucide-react";
import { resolveProductImage } from "../api/agent";
import type { CartView } from "../types";

interface CartPanelProps {
  cart: CartView | null;
  open: boolean;
  disabled: boolean;
  onClose: () => void;
  onAction: (message: string) => void;
  onUpdateQuantity: (itemId: string, qty: number) => void;
  onRemoveItem: (itemId: string) => void;
}

function money(value: string | number) {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

export function CartPanel({ cart, open, disabled, onClose, onAction, onUpdateQuantity, onRemoveItem }: CartPanelProps) {
  const items = cart?.items ?? [];
  return (
    <aside className={`cart-panel ${open ? "cart-panel--open" : ""}`} aria-label="Shopping cart">
      <div className="cart-panel__header">
        <div>
          <span className="section-kicker">Your selection</span>
          <h2>Shopping bag</h2>
        </div>
        <button type="button" className="icon-button cart-panel__close" onClick={onClose} aria-label="Close cart">
          <X size={19} />
        </button>
      </div>

      <div className="cart-panel__body">
        {items.length === 0 ? (
          <div className="cart-empty">
            <div className="cart-empty__icon"><ShoppingBag size={28} /></div>
            <h3>Your bag is empty</h3>
            <p>Ask the stylist to find something, then add any displayed option.</p>
            <button type="button" className="button button--outline" disabled={disabled} onClick={() => onAction("Browse shirts")}>Browse products</button>
          </div>
        ) : (
          <div className="cart-items">
            {items.map((item) => {
              const image = resolveProductImage(item.image_url);
              return (
                <article className="cart-item" key={item.item_id}>
                  <div className="cart-item__image">
                    {image ? <img src={image} alt={item.product_name} /> : <ShoppingBag size={22} />}
                  </div>
                  <div className="cart-item__info">
                    <h3>{item.product_name}</h3>
                    <p>{item.color} · Size {item.size}</p>
                    <strong>{money(item.line_total)}</strong>
                    <div className="cart-item__controls">
                      <button
                        type="button"
                        aria-label={`Decrease ${item.product_name} quantity`}
                        disabled={disabled}
                        onClick={() => item.quantity === 1
                          ? onRemoveItem(item.item_id)
                          : onUpdateQuantity(item.item_id, item.quantity - 1)}
                      >
                        <Minus size={14} />
                      </button>
                      <span>{item.quantity}</span>
                      <button
                        type="button"
                        aria-label={`Increase ${item.product_name} quantity`}
                        disabled={disabled || item.quantity >= 10}
                        onClick={() => onUpdateQuantity(item.item_id, item.quantity + 1)}
                      >
                        <Plus size={14} />
                      </button>
                      <button
                        type="button"
                        className="cart-item__remove"
                        aria-label={`Remove ${item.product_name}`}
                        disabled={disabled}
                        onClick={() => onRemoveItem(item.item_id)}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>

      <div className="cart-panel__footer">
        <div className="cart-total-row">
          <span>Subtotal</span>
          <strong>{money(cart?.subtotal ?? 0)}</strong>
        </div>
        <p>Checkout happens through the Agent in V1.</p>
        {items.length > 0 && (
          <div style={{ display: "flex", gap: "10px", marginTop: "16px", flexDirection: "column" }}>
            <button type="button" className="button button--primary" disabled={disabled} onClick={() => {
              onAction("Checkout my cart");
              onClose();
            }}>
              Checkout
            </button>
            <button type="button" className="button button--danger" disabled={disabled} onClick={() => onAction("Clear my cart")}>
              Clear bag
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
