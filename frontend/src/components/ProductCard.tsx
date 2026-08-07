import { Check, PackageCheck, ShoppingBag } from "lucide-react";
import { useEffect, useState } from "react";
import { resolveProductImage } from "../api/agent";
import type { ProductOption } from "../types";

interface ProductCardProps {
  product: ProductOption;
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
  const resolvedImage = resolveProductImage(product.image_url);
  const [imageFailed, setImageFailed] = useState(false);

  useEffect(() => setImageFailed(false), [resolvedImage]);

  const image = resolvedImage && !imageFailed ? resolvedImage : null;
  const primaryReason = product.match_reasons[0] || (product.available_quantity > 0 ? "In stock" : null);

  return (
    <article className="product-card">
      <div className="product-card__media">
        {image ? (
          <img
            src={image}
            alt={product.product_name}
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={() => {
              console.warn("Product image failed to load", {
                productId: product.product_id,
                imageUrl: resolvedImage,
              });
              setImageFailed(true);
            }}
          />
        ) : (
          <div className="product-card__placeholder" aria-label="Product image unavailable">
            <ShoppingBag size={34} strokeWidth={1.4} />
            <span>Image unavailable</span>
          </div>
        )}
        <span className="product-card__position">Option {position}</span>
        {primaryReason && <span className="product-card__match">{primaryReason}</span>}
      </div>

      <div className="product-card__body">
        <div className="product-card__eyebrow">
          <span>{product.brand}</span>
          <span>{product.article_code}</span>
        </div>
        <h3>{product.product_name}</h3>
        <div className="product-card__price-row">
          <p className="product-card__price">{formatCurrency(product.price)}</p>
          <span className="product-card__availability">
            <PackageCheck size={13} /> {product.available_quantity}
          </span>
        </div>

        <div className="product-card__variants">
          <span>{product.color}</span>
          <span>Size {product.size}</span>
          {product.fit && <span>{product.fit}</span>}
        </div>

        {product.match_reasons.length > 0 && (
          <div className="product-card__matches">
            {product.match_reasons.slice(0, 2).map((reason) => (
              <span key={reason}><Check size={12} /> {reason}</span>
            ))}
          </div>
        )}

        <div className="product-card__actions">
          <button
            type="button"
            className="button button--primary"
            disabled={disabled}
            onClick={() => onAction(`Add option ${position} to my cart`)}
          >
            <ShoppingBag size={15} /> Add
          </button>
          <button
            type="button"
            className="button button--ghost"
            disabled={disabled}
            onClick={() => onAction(`Tell me more about option ${position}`)}
          >
            Details
          </button>
        </div>
      </div>
    </article>
  );
}
