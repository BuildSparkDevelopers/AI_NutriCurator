import { Product } from "@/lib/types";

const PRODUCTS_API_BASE = "/api/v1/products";
const FALLBACK_IMAGE_URL = "https://picsum.photos/seed/product-placeholder/400/500";

type ProductListApiItem = {
  product_id: number | string;
  name?: string | null;
  category?: string | null;
  brand?: string | null;
  price?: number | null;
  image_url?: string | null;
};

type ProductDetailApiItem = ProductListApiItem & {
  description?: string | null;
  ingredients?: string[] | null;
  allergy?: string | null;
  calories?: number | null;
  sodium?: number | null;
  carbohydrate?: number | null;
  sugar?: number | null;
  fat?: number | null;
  trans_fat?: number | null;
  saturated_fat?: number | null;
  cholesterol?: number | null;
  protein?: number | null;
};

type ProductListApiResponse = {
  total: number;
  limit: number;
  offset: number;
  items: ProductListApiItem[];
};

function toNumber(value: number | string | null | undefined, fallback = 0): number {
  const n = Number(value);
  return Number.isFinite(n) ? n : fallback;
}

function toImageUrl(value?: string | null): string {
  if (!value) return FALLBACK_IMAGE_URL;
  return value;
}

function toNutrition(detail: ProductDetailApiItem): Product["nutrition"] {
  return {
    rawmtrl: (detail.ingredients ?? []).join(", "),
    allergymtrl: detail.allergy ?? "",
    serving_size: 100,
    reference_intake: 1,
    food_weight: 100,
    calories_kcal: toNumber(detail.calories),
    protein_g: toNumber(detail.protein),
    fat_g: toNumber(detail.fat),
    ash_g: 0,
    carbohydrate_g: toNumber(detail.carbohydrate),
    sugar_g: toNumber(detail.sugar),
    sodium_mg: toNumber(detail.sodium),
    cholesterol_mg: toNumber(detail.cholesterol),
    saturated_fat_g: toNumber(detail.saturated_fat),
    trans_fat_g: toNumber(detail.trans_fat),
    gi: 0,
    gl: 0,
  };
}

function mapSummaryToProduct(item: ProductListApiItem, categoryId: number | null = null): Product {
  const price = toNumber(item.price, 0);
  return {
    product_id: toNumber(item.product_id),
    name: item.name ?? "이름 없는 상품",
    brand: item.brand ?? "",
    category_id: categoryId ?? 0,
    category: item.category ?? null,
    image_url: toImageUrl(item.image_url),
    is_active: true,
    quantity: 1,
    price,
    discount_rate: 0,
    original_price: price,
    created_at: "",
    updated_at: "",
    nutrition: {
      rawmtrl: "",
      allergymtrl: "",
      serving_size: 100,
      reference_intake: 1,
      food_weight: 100,
      calories_kcal: 0,
      protein_g: 0,
      fat_g: 0,
      ash_g: 0,
      carbohydrate_g: 0,
      sugar_g: 0,
      sodium_mg: 0,
      cholesterol_mg: 0,
      saturated_fat_g: 0,
      trans_fat_g: 0,
      gi: 0,
      gl: 0,
    },
    description: "",
  };
}

function mapDetailToProduct(item: ProductDetailApiItem): Product {
  const price = toNumber(item.price, 0);
  return {
    product_id: toNumber(item.product_id),
    name: item.name ?? "이름 없는 상품",
    brand: item.brand ?? "",
    category_id: 0,
    category: item.category ?? null,
    image_url: toImageUrl(item.image_url),
    is_active: true,
    quantity: 1,
    price,
    discount_rate: 0,
    original_price: price,
    created_at: "",
    updated_at: "",
    nutrition: toNutrition(item),
    description: item.description ?? "",
  };
}

export async function fetchProducts(params?: {
  categoryId?: number | null;
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<{ total: number; items: Product[] }> {
  const query = new URLSearchParams();
  if (params?.categoryId !== undefined && params.categoryId !== null) {
    query.set("category", String(params.categoryId));
  }
  if (params?.q) query.set("q", params.q);
  query.set("limit", String(params?.limit ?? 40));
  query.set("offset", String(params?.offset ?? 0));

  const res = await fetch(`${PRODUCTS_API_BASE}?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error("상품 목록을 불러오지 못했습니다.");
  }

  const data = (await res.json()) as ProductListApiResponse;
  const items = (data.items ?? []).map((item) => mapSummaryToProduct(item, params?.categoryId ?? null));
  return { total: data.total ?? items.length, items };
}

export async function fetchProductDetail(productId: number): Promise<Product> {
  const res = await fetch(`${PRODUCTS_API_BASE}/${productId}`, { cache: "no-store" });
  if (!res.ok) {
    if (res.status === 404) throw new Error("NOT_FOUND");
    throw new Error("상품 상세를 불러오지 못했습니다.");
  }
  const data = (await res.json()) as ProductDetailApiItem;
  return mapDetailToProduct(data);
}
