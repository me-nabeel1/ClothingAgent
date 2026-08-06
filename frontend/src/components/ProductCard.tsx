import { Check, MapPin, PackageCheck, ShoppingBag } from "lucide-react";
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
  const image = resolveProductImage(product.image_url);
  return (
    <article className="product-card">
      <div className="product-card__media">
        {image ? (
          <img src={image} alt={product.product_name} loading="lazy" />
        ) : (
          <div className="product-card__placeholder" aria-label="No product image">
            <ShoppingBag size={32} strokeWidth={1.5} />
          </div>
        )}
        <span className="product-card__position">Option {position}</span>
        <span className="product-card__stock">
          <PackageCheck size={13} /> {product.available_quantity} available
        </span>
      </div>

      <div className="product-card__body">
        <div className="product-card__eyebrow">
          <span>{product.brand}</span>
          <span>{product.article_code}</span>
        </div>
        <h3>
          <a href={`/dummy-product/${product.product_id}`} target="_blank" rel="noreferrer" style={{color: 'inherit', textDecoration: 'none'}}>
            {product.product_name}
          </a>
        </h3>
        <p className="product-card__price">{formatCurrency(product.price)}</p>

        <div className="product-card__variants">
          <span>{product.color}</span>
          <span>Size {product.size}</span>
          {product.fit && <span>{product.fit}</span>}
        </div>

        <p className="product-card__branch">
          <MapPin size={14} /> {product.branch_name}, {product.city}
        </p>

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
            <ShoppingBag size={16} /> Add to cart
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
