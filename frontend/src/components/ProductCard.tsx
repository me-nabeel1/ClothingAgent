import { Check, PackageCheck, ShoppingBag } from "lucide-react";
import { useEffect, useState } from "react";
import { resolveProductImage } from "../api/agent";
import { ProductDetailsModal } from "./ProductDetailsModal";
import type { ProductView } from "../types";

interface ProductCardProps {
  product: ProductView;
  position: number;
  disabled: boolean;
  onAction: (message: string) => void;
}

function formatCurrency(value: string | number) {
  return new Intl.NumberFormat("en-PK", {
    style: "currency",
    currency: "PKR",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

export function ProductCard({ product, position, disabled, onAction }: ProductCardProps) {
  const primaryImage = product.images?.[0] || null;
  const resolvedImage = resolveProductImage(primaryImage);
  const [imageFailed, setImageFailed] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  useEffect(() => setImageFailed(false), [resolvedImage]);

  const image = resolvedImage && !imageFailed ? resolvedImage : null;
  
  // Aggregate available quantities across variants
  const totalQuantity = product.variants?.reduce((sum, v) => {
    return sum + v.branch_availability.reduce((bsum, b) => bsum + b.available_quantity, 0);
  }, 0) || 0;
  
  const inStock = totalQuantity > 0;
  const primaryReason = inStock ? "In stock" : "Out of stock";

  // Get distinct sizes and colors
  const sizes = Array.from(new Set(product.variants?.map(v => v.size) || []));
  const colors = Array.from(new Set(product.variants?.map(v => v.color) || []));

  return (
    <article className={`product-card ${!inStock ? "product-card--out-of-stock" : ""}`}>
      <div className="product-card__media">
        {image ? (
          <img
            src={image}
            alt={product.product_name}
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="product-card__placeholder" aria-label="Product image unavailable">
            <ShoppingBag size={34} strokeWidth={1.4} />
            <span>Image unavailable</span>
          </div>
        )}
        <span className="product-card__position">Option {position}</span>
        <span className="product-card__match">{primaryReason}</span>
      </div>

      <div className="product-card__body">
        <div className="product-card__eyebrow">
          <span>{product.brand}</span>
          <span>{product.article_code}</span>
        </div>
        <h3>{product.product_name}</h3>
        
        <div className="product-card__price-row">
          <div className="product-card__prices">
            <span className="product-card__price">{formatCurrency(product.final_price)}</span>
            {Number(product.discount_amount) > 0 && (
              <span className="product-card__original-price">{formatCurrency(product.base_price)}</span>
            )}
          </div>
          {inStock && (
            <span className="product-card__availability">
              <PackageCheck size={13} /> {totalQuantity} left
            </span>
          )}
        </div>

        {Number(product.discount_amount) > 0 && product.applied_offer && (
          <div className="product-card__discount-badge">
            {product.applied_offer.offer_name || product.applied_offer.offer_code}
          </div>
        )}

        <div className="product-card__variants">
          {colors.length > 0 && <span>{colors.join(" • ")}</span>}
          {sizes.length > 0 && <span>Sizes: {sizes.join(" • ")}</span>}
        </div>

        <div className="product-card__actions">
          <button
            type="button"
            className="button button--primary"
            disabled={disabled || !inStock}
            onClick={() => onAction(`Add option ${position} to my cart`)}
          >
            <ShoppingBag size={15} /> {inStock ? "Add" : "Out of stock"}
          </button>
          <button
            type="button"
            className="button button--ghost"
            disabled={disabled}
            onClick={() => {
              setDetailsOpen(true);
              onAction(`Tell me more about option ${position}`);
            }}
          >
            Details
          </button>
        </div>
      </div>
      <ProductDetailsModal
        product={product}
        open={detailsOpen}
        onClose={() => setDetailsOpen(false)}
      />
    </article>
  );
}
