export interface Nutrition {
  rawmtrl: string;
  allergymtrl: string;
  serving_size: number;
  reference_intake: number;
  food_weight: number;
  calories_kcal: number;
  protein_g: number;
  fat_g: number;
  ash_g: number;
  carbohydrate_g: number;
  sugar_g: number;
  sodium_mg: number;
  cholesterol_mg: number;
  saturated_fat_g: number;
  trans_fat_g: number;
  gi: number;
  gl: number;
}

export interface Product {
  product_id: number;
  name: string;
  brand: string;
  category_id: number;
  image_url: string;
  is_active: boolean;
  quantity: number;
  price: number;
  discount_rate: number;
  original_price: number;
  created_at: string;
  updated_at: string;
  nutrition: Nutrition;
  description?: string;
}

export interface Category {
  category_id: number;
  name: string;
  supercategory: string;
}

export interface User {
  user_id: number;
  email: string;
  created_at: string;
  updated_at: string;
  is_sensitive_agreed: boolean;
  agreed_at: string;
  is_tos_agreed: boolean;
  is_privacy_agreed: boolean;
}

export interface UserHealthProfile {
  user_id: number;
  gender: string;
  birth_date: string;
  height: number;
  weight: number;
  average_of_steps: number;
  activity_level: string;
  diabetes: string;
  hypertension: string;
  kidneydisease: string;
  allergy: string;
  notes: string;
  favorite: string;
  goal: string;
}

export interface CartItem {
  cart_item_id: number;
  product: Product;
  quantity: number;
  checked: boolean;
  ai_decision?: "safe" | "caution" | "warning";
  ai_reason?: string;
}

export interface AIAnalysisResult {
  log_id: number;
  user_id: number;
  product_id: number;
  decision: "safe" | "caution" | "warning";
  reason_summary: string;
  alternatives?: number[];
  created_at: string;
}
