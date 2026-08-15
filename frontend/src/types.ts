export type MessageRole = "user" | "assistant";

// ---------------------------------------------------------------------------
// V1 Catalog & Product Types
// ---------------------------------------------------------------------------

export interface OfferSummary {
  offer_code: string;
  offer_name: string;
  description: string | null;
  discount_amount: number | string | null;
  discount_percentage: number | string | null;
  benefit_type: string;
}

export interface BranchAvailabilityView {
  branch_id: number;
  branch_code: string;
  branch_name: string;
  is_available: boolean;
  available_quantity: number;
}

export interface VariantView {
  variant_id: number;
  sku: string;
  color: string;
  size: string;
  price: number | string;
  final_price: number | string;
  discount_amount: number | string;
  applied_offer: OfferSummary | null;
  is_available: boolean;
  branch_availability: BranchAvailabilityView[];
}

export interface ProductView {
  product_id: number;
  article_code: string;
  product_name: string;
  description: string | null;
  category: string;
  subcategory: string | null;
  product_type: string;
  gender: string;
  brand: string;
  material: string | null;
  fit: string | null;
  season: string | null;
  occasion: string | null;
  base_price: number | string;
  final_price: number | string;
  discount_amount: number | string;
  applied_offer: OfferSummary | null;
  images: string[];
  variants: VariantView[];
}

export interface ProductDetails {
  product: ProductView;
}

// ---------------------------------------------------------------------------
// V1 Cart Types
// ---------------------------------------------------------------------------

export interface CartItem {
  item_id: string;
  product_id: number;
  variant_id: number;
  branch_id: number;
  article_code: string;
  product_name: string;
  color: string;
  size: string;
  quantity: number;
  unit_price: number | string;
  line_total: number | string;
  image_url: string | null;
}

export interface CartView {
  cart_id: string;
  items: CartItem[];
  total_quantity: number;
  subtotal: number | string;
  created_at: string;
  updated_at: string;
  expires_at: string;
}

// ---------------------------------------------------------------------------
// V1 Agent State Types
// ---------------------------------------------------------------------------

export interface DisplayedProduct {
  product_id: number;
  article_code: string;
  product_name: string;
}

export interface Budget {
  minimum: number | null;
  maximum: number | null;
}

export interface CartContext {
  cart_id: string | null;
  item_count: number;
  subtotal: number;
}

export interface DeliveryContext {
  customer_name: string | null;
  phone: string | null;
  delivery_address: string | null;
  city: string | null;
  delivery_notes: string | null;
}

export interface ConversationState {
  session_id: string;
  conversation_stage: string;
  current_intent: string | null;
  categories: string[];
  occasions: string[];
  product_types: string[];
  preferred_colors: string[];
  excluded_colors: string[];
  materials: string[];
  fits: string[];
  budget: Budget;
  branch_preference: string | null;
  size_preferences: Record<string, string>;
  displayed_products: DisplayedProduct[];
  selected_product_id: number | null;
  cart: CartContext;
  delivery: DeliveryContext;
  order_confirmed: boolean;
}

export interface ChatResponse {
  reply: string;
  state: ConversationState;
}

// ---------------------------------------------------------------------------
// UI State Types
// ---------------------------------------------------------------------------

export interface TimelineMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  products?: ProductView[];
  checkoutPreview?: any;
  deliveryContext?: DeliveryContext;
}

export interface HealthStatus {
  agent: "checking" | "online" | "offline";
  clothingApp: "checking" | "online" | "offline";
  llm: "configured" | "local_fallback" | "unknown";
}
