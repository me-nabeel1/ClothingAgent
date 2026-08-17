import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { getMenu, resolveProductImage } from "../api/agent";
import type { ProductView } from "../types";

interface MenuLandingProps {
  onEnterAgent: (message?: string) => void;
}

export function MenuLanding({ onEnterAgent }: MenuLandingProps) {
  const [categories, setCategories] = useState<{ category_name: string; products: ProductView[] }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMenu()
      .then((res) => setCategories(res.categories || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="menu-landing" style={{ width: "100%", height: "100%", overflowY: "auto", padding: "32px 40px", paddingBottom: "120px" }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto", textAlign: "center", marginBottom: "40px" }}>
        <h1 style={{ fontFamily: "Georgia, serif", fontSize: "42px", fontWeight: "500", margin: "0 0 16px" }}>
          Discover the Collection
        </h1>
        <p style={{ color: "var(--muted)", fontSize: "16px", maxWidth: "600px", margin: "0 auto 32px", lineHeight: "1.6" }}>
          Browse our curated selections below. Need help finding something specific? Our AI Stylist is here to assist you.
        </p>
        <button
          type="button"
          className="button button--primary"
          style={{ padding: "0 24px", height: "48px", fontSize: "15px", borderRadius: "99px", boxShadow: "0 10px 30px rgba(49,88,72,.2)" }}
          onClick={() => onEnterAgent()}
        >
          <Sparkles size={18} /> Chat with AI Stylist
        </button>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "40px 0" }}>
          <div className="typing-indicator" style={{ display: "inline-flex", background: "transparent", border: "none" }}>
            <span /><span /><span />
          </div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "48px", maxWidth: "1200px", margin: "0 auto" }}>
          {categories.map((cat) => (
            <div key={cat.category_name}>
              <h3 style={{ margin: "0 0 20px", fontFamily: "Georgia, serif", fontSize: "24px" }}>
                {cat.category_name}
              </h3>
              <div className="carousel-container" style={{ display: "flex", overflowX: "auto", gap: "20px", paddingBottom: "16px", scrollSnapType: "x mandatory" }}>
                {cat.products.map((product) => {
                  const image = resolveProductImage(product.images?.[0] || null);
                  return (
                    <article
                      key={product.product_id}
                      className="product-card"
                      style={{ flex: "0 0 220px", cursor: "pointer", scrollSnapAlign: "start" }}
                      onClick={() => onEnterAgent(`Show me this ${product.product_name}`)}
                    >
                      <div className="product-card__media" style={{ borderRadius: "18px 18px 0 0" }}>
                        {image ? <img src={image} alt={product.product_name} style={{ mixBlendMode: "multiply" }} /> : <div className="product-card__placeholder">No image</div>}
                      </div>
                      <div className="product-card__body" style={{ padding: "12px 16px" }}>
                        <div style={{ fontSize: "14px", fontWeight: "600", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", marginBottom: "4px" }}>
                          {product.product_name}
                        </div>
                        <div style={{ fontSize: "13px", color: "var(--muted)" }}>{Math.round(Number(product.final_price) || 0)} rupees</div>
                      </div>
                    </article>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
