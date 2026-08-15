import { Bot, UserRound, ArrowRight } from "lucide-react";
import type { TimelineMessage } from "../types";
import { ProductCard } from "./ProductCard";
import { useState } from "react";

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

function formatCurrency(value: string | number) {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

export function MessageBubble({ message, disabled, onAction }: MessageBubbleProps) {
  const assistant = message.role === "assistant";
  
  // Detect Urdu script to determine text direction
  const isUrdu = /[\u0600-\u06FF]/.test(message.content);
  const textDirection = isUrdu ? "rtl" : "ltr";
  const textAlign = isUrdu ? "right" : "left";

  const [deliveryData, setDeliveryData] = useState({
    name: message.deliveryContext?.customer_name || "",
    phone: message.deliveryContext?.phone || "",
    city: message.deliveryContext?.city || "",
    address: message.deliveryContext?.delivery_address || "",
    notes: message.deliveryContext?.delivery_notes || "",
  });

  const handleDeliverySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formattedMessage = `Place order with corrected details:\nName: ${deliveryData.name}\nPhone: ${deliveryData.phone}\nCity: ${deliveryData.city}\nAddress: ${deliveryData.address}`;
    onAction(formattedMessage);
  };

  return (
    <div className={`message-row ${assistant ? "message-row--assistant" : "message-row--user"}`}>
      <div className="message-avatar" aria-hidden="true">
        {assistant ? <Bot size={17} /> : <UserRound size={17} />}
      </div>
      <div className="message-content">
        <div 
          className="message-bubble" 
          dir={textDirection} 
          style={{ textAlign }}
        >
          <p style={{ whiteSpace: "pre-wrap" }}>{message.content}</p>
          <span className="message-time">{formatTime(message.createdAt)}</span>
        </div>

        {message.products && message.products.length > 0 && (
          <div className="product-grid" dir="ltr">
            {message.products.map((product, index) => (
              <ProductCard
                key={`${product.product_id}-${index}`}
                product={product}
                position={index + 1}
                disabled={disabled}
                onAction={onAction}
              />
            ))}
          </div>
        )}

        {message.checkoutPreview && (
          <div className="checkout-preview-card" dir="ltr">
            <h4>Order Summary</h4>
            <div className="checkout-preview-row">
              <span>Subtotal</span>
              <span>{formatCurrency(message.checkoutPreview.subtotal)}</span>
            </div>
            {message.checkoutPreview.discount_total > 0 && (
              <div className="checkout-preview-row discount">
                <span>Discount</span>
                <span>-{formatCurrency(message.checkoutPreview.discount_total)}</span>
              </div>
            )}
            <div className="checkout-preview-row">
              <span>Delivery Fee</span>
              <span>
                {message.checkoutPreview.delivery_fee === 0 || message.checkoutPreview.delivery_fee === "0" || message.checkoutPreview.delivery_fee === "0.00"
                  ? "FREE"
                  : formatCurrency(message.checkoutPreview.delivery_fee)}
              </span>
            </div>
            <div className="checkout-preview-row total">
              <span>Grand Total</span>
              <span>{formatCurrency(message.checkoutPreview.grand_total)}</span>
            </div>
            {message.checkoutPreview.applied_promotions?.length > 0 && (
              <div className="checkout-preview-promos">
                <strong>Applied Offers:</strong>
                <ul>
                  {message.checkoutPreview.applied_promotions.map((promo: any, idx: number) => (
                    <li key={idx}>{promo.offer_name || promo.offer_code}</li>
                  ))}
                </ul>
              </div>
            )}

            {message.deliveryContext && (
              <div className="delivery-form-container">
                <h5>Confirm Delivery Details</h5>
                <form onSubmit={handleDeliverySubmit} className="delivery-form">
                  <div className="delivery-form-group">
                    <label>Name</label>
                    <input 
                      type="text" 
                      value={deliveryData.name} 
                      onChange={(e) => setDeliveryData({...deliveryData, name: e.target.value})}
                      required
                      disabled={disabled}
                    />
                  </div>
                  <div className="delivery-form-group">
                    <label>Phone</label>
                    <input 
                      type="text" 
                      value={deliveryData.phone} 
                      onChange={(e) => setDeliveryData({...deliveryData, phone: e.target.value})}
                      required
                      disabled={disabled}
                    />
                  </div>
                  <div className="delivery-form-group">
                    <label>City</label>
                    <input 
                      type="text" 
                      value={deliveryData.city} 
                      onChange={(e) => setDeliveryData({...deliveryData, city: e.target.value})}
                      required
                      disabled={disabled}
                    />
                  </div>
                  <div className="delivery-form-group">
                    <label>Address</label>
                    <textarea 
                      value={deliveryData.address} 
                      onChange={(e) => setDeliveryData({...deliveryData, address: e.target.value})}
                      required
                      disabled={disabled}
                    />
                  </div>
                  <div className="checkout-preview-actions">
                    <button 
                      type="submit"
                      className="button button--primary"
                      disabled={disabled}
                    >
                      Confirm Details & Place Order <ArrowRight size={14} />
                    </button>
                  </div>
                </form>
              </div>
            )}
            {!message.deliveryContext && (
              <div className="checkout-preview-actions">
                <button 
                  className="button button--primary"
                  disabled={disabled}
                  onClick={() => onAction("Yes, I confirm the order.")}
                >
                  Confirm Order <ArrowRight size={14} />
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
