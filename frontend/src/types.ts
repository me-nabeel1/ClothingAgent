export type MessageRole = "user" | "assistant";

export interface ConversationMessage {
  message_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface ConversationView {
  conversation_id: string;
  cart_id: string | null;
  messages: ConversationMessage[];
  active_agent: string;
  current_intent: string;
  shopping_stage: string;
  created_at: string;
  updated_at: string;
}

export interface ProductOption {
  product_id: number;
  variant_id: number;
  branch_id: number;
  article_code: string;
  product_name: string;
  category: string;
  gender: string;
  brand: string;
  color: string;
  size: string;
  price: string | number;
  branch_code: string;
  branch_name: string;
  city: string;
  available_quantity: number;
  in_transit_quantity: number;
  image_url: string | null;
  material: string | null;
  fit: string | null;
  season: string | null;
  tags: string[];
  description: string | null;
  match_score: number;
  match_reasons: string[];
}

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
  unit_price: string | number;
  line_total: string | number;
  image_url: string | null;
}

export interface CartView {
  cart_id: string;
  items: CartItem[];
  total_quantity: number;
  subtotal: string | number;
  created_at: string;
  updated_at: string;
  expires_at: string;
}

export interface ConversationStarted {
  conversation: ConversationView;
  suggested_actions: string[];
}

export interface ChatTurnResponse {
  conversation_id: string;
  message_id: string;
  reply: string;
  active_agent: string;
  intent: string;
  products: ProductOption[];
  cart: CartView | null;
  suggested_actions: string[];
  ui_actions: string[];
}

export interface TimelineMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  products?: ProductOption[];
  suggestedActions?: string[];
  activeAgent?: string;
  intent?: string;
  uiActions?: string[];
}

export interface HealthStatus {
  agent: "checking" | "online" | "offline";
  clothingApp: "checking" | "online" | "offline";
  llm: "configured" | "local_fallback" | "unknown";
}
