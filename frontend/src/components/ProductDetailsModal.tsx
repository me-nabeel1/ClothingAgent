import { X } from "lucide-react";
import { resolveProductImage } from "../api/agent";
import type { ProductOption } from "../types";

interface ProductDetailsModalProps {
  product: ProductOption | null;
  open: boolean;
  onClose: () => void;
}

export function ProductDetailsModal({ product, open, onClose }: ProductDetailsModalProps) {
  if (!product) return null;

  const image = resolveProductImage(product.image_url);

  return (
    <>
      {open && (
        <button
          className="cart-backdrop"
          type="button"
          aria-label="Close details"
          onClick={onClose}
          style={{ zIndex: 100 }}
        />
      )}
      <div
        className={`cart-panel ${open ? "cart-panel--open" : ""}`}
        style={{ zIndex: 110, width: "min(460px, calc(100vw - 32px))", left: "50%", transform: open ? "translate(-50%, -50%)" : "translate(-50%, -40%)", top: "50%", opacity: open ? 1 : 0, transition: "all .24s ease", height: "auto", maxHeight: "90vh", bottom: "auto" }}
        role="dialog"
        aria-label="Product Details"
      >
        <div className="cart-panel__header" style={{ padding: "16px 20px" }}>
          <div>
            <span className="section-kicker">{product.brand}</span>
            <h2 style={{ fontSize: "18px" }}>{product.product_name}</h2>
          </div>
          <button type="button" className="icon-button cart-panel__close" onClick={onClose} aria-label="Close details">
            <X size={19} />
          </button>
        </div>

        <div className="cart-panel__body" style={{ padding: "20px" }}>
          <div style={{ display: "flex", gap: "16px", marginBottom: "20px" }}>
            <div className="product-card__media" style={{ width: "120px", borderRadius: "12px", flexShrink: 0 }}>
              {image ? <img src={image} alt={product.product_name} style={{ mixBlendMode: "multiply" }} /> : <div className="product-card__placeholder">No image</div>}
            </div>
            <div>
              <div style={{ fontSize: "18px", fontWeight: "700", marginBottom: "8px" }}>PKR {product.price}</div>
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Color: <strong style={{ color: "var(--ink)" }}>{product.color}</strong></div>
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Size: <strong style={{ color: "var(--ink)" }}>{product.size}</strong></div>
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Stock: <strong style={{ color: "var(--ink)" }}>{product.available_quantity} available</strong></div>
            </div>
          </div>

          <div style={{ marginBottom: "20px" }}>
            <h4 style={{ margin: "0 0 8px", fontSize: "14px", fontWeight: "600" }}>Description</h4>
            <p style={{ margin: 0, fontSize: "13px", lineHeight: "1.5", color: "var(--muted)" }}>
              {product.description || "No description available."}
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px", marginBottom: "20px" }}>
            <div>
              <div style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".05em" }}>Category</div>
              <div style={{ fontSize: "13px", fontWeight: "500" }}>{product.category}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".05em" }}>Material</div>
              <div style={{ fontSize: "13px", fontWeight: "500" }}>{product.material || "N/A"}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".05em" }}>Fit</div>
              <div style={{ fontSize: "13px", fontWeight: "500" }}>{product.fit || "N/A"}</div>
            </div>
            <div>
              <div style={{ fontSize: "11px", color: "var(--muted)", textTransform: "uppercase", letterSpacing: ".05em" }}>Season</div>
              <div style={{ fontSize: "13px", fontWeight: "500" }}>{product.season || "N/A"}</div>
            </div>
          </div>

          {product.tags.length > 0 && (
            <div>
              <h4 style={{ margin: "0 0 8px", fontSize: "14px", fontWeight: "600" }}>Tags</h4>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {product.tags.map(tag => (
                  <span key={tag} style={{ padding: "4px 8px", background: "var(--paper-soft)", borderRadius: "6px", fontSize: "11px", color: "var(--ink-soft)", border: "1px solid var(--line)" }}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
