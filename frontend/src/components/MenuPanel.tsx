import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { getMenu, resolveProductImage } from "../api/agent";
import type { ProductView } from "../types";

interface MenuPanelProps {
  open: boolean;
  onClose: () => void;
  onAction: (message: string) => void;
}

export function MenuPanel({ open, onClose, onAction }: MenuPanelProps) {
  const [categories, setCategories] = useState<{ category_name: string; products: ProductView[] }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open && categories.length === 0) {
      setLoading(true);
      getMenu()
        .then((res) => setCategories(res.categories || []))
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [open, categories.length]);

  return (
    <aside className={`cart-panel ${open ? "cart-panel--open" : ""}`} style={{ zIndex: 60, width: "min(600px, calc(100vw - 32px))" }} aria-label="Catalog Menu">
      <div className="cart-panel__header">
        <div>
          <span className="section-kicker">Catalog</span>
          <h2>Our Collection</h2>
        </div>
        <button type="button" className="icon-button cart-panel__close" onClick={onClose} aria-label="Close menu">
          <X size={19} />
        </button>
      </div>

      <div className="cart-panel__body">
        {loading ? (
          <div className="cart-empty">
            <div className="typing-indicator" style={{ display: "inline-flex" }}>
              <span /><span /><span />
            </div>
            <p style={{ marginTop: "16px" }}>Loading catalog...</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {categories.map((cat) => (
              <div key={cat.category_name}>
                <h3 style={{ margin: "0 0 12px", fontFamily: "Georgia, serif" }}>{cat.category_name}</h3>
                <div style={{ display: "flex", overflowX: "auto", gap: "12px", paddingBottom: "8px" }}>
                  {cat.products.map((product) => {
                    const image = resolveProductImage(product.images?.[0] || null);
                    return (
                      <div key={product.product_id} style={{ flex: "0 0 140px", cursor: "pointer" }} onClick={() => {
                        onAction(`Show me this ${product.product_name}`);
                        onClose();
                      }}>
                        <div className="product-card__media" style={{ borderRadius: "12px", marginBottom: "8px" }}>
                          {image ? <img src={image} alt={product.product_name} style={{ mixBlendMode: "multiply" }} /> : <div className="product-card__placeholder">No image</div>}
                        </div>
                        <div style={{ fontSize: "12px", fontWeight: "600", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{product.product_name}</div>
                        <div style={{ fontSize: "11px", color: "var(--muted)" }}>{Math.round(Number(product.final_price) || 0)} rupees</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
