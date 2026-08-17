import { X } from "lucide-react";
import { resolveProductImage } from "../api/agent";
import type { ProductView } from "../types";

interface ProductDetailsModalProps {
  product: ProductView | null;
  open: boolean;
  onClose: () => void;
}

function formatCurrency(value: string | number) {
  const num = Math.round(Number(value) || 0);
  return `${num.toLocaleString()} rupees`;
}

export function ProductDetailsModal({ product, open, onClose }: ProductDetailsModalProps) {
  if (!product) return null;

  const primaryImage = product.images?.[0] || null;
  const image = resolveProductImage(primaryImage);

  const sizes = Array.from(new Set(product.variants?.map(v => v.size) || []));
  const colors = Array.from(new Set(product.variants?.map(v => v.color) || []));
  
  const totalQuantity = product.variants?.reduce((sum, v) => {
    return sum + v.branch_availability.reduce((bsum, b) => bsum + b.available_quantity, 0);
  }, 0) || 0;

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
              <div style={{ fontSize: "18px", fontWeight: "700", marginBottom: "8px" }}>{formatCurrency(product.final_price)}</div>
              {Number(product.discount_amount) > 0 && (
                <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px", textDecoration: "line-through" }}>
                  {formatCurrency(product.base_price)}
                </div>
              )}
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Colors: <strong style={{ color: "var(--ink)" }}>{colors.join(", ")}</strong></div>
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Sizes: <strong style={{ color: "var(--ink)" }}>{sizes.join(", ")}</strong></div>
              <div style={{ fontSize: "13px", color: "var(--muted)", marginBottom: "4px" }}>Stock: <strong style={{ color: "var(--ink)" }}>{totalQuantity} available</strong></div>
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
        </div>
      </div>
    </>
  );
}
