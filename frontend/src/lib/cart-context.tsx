"use client";

import {
  createContext,
  useContext,
  useState,
  useCallback,
  useMemo,
  useEffect,
  useRef,
  ReactNode,
} from "react";
import { CartItem, Product } from "./types";

const CART_STORAGE_KEY = "nutricurator_cart";

function loadStoredCart(): CartItem[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as CartItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveCart(items: CartItem[]) {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(items));
  } catch {}
}

interface CartContextType {
  items: CartItem[];
  addItem: (product: Product, aiDecision?: CartItem["ai_decision"], aiReason?: string) => void;
  removeItem: (cartItemId: number) => void;
  updateQuantity: (cartItemId: number, quantity: number) => void;
  toggleCheck: (cartItemId: number) => void;
  toggleCheckAll: (checked: boolean) => void;
  removeChecked: () => void;
  totalCount: number;
  checkedItems: CartItem[];
  productTotal: number;
  discountTotal: number;
  finalTotal: number;
  deliveryFee: number;
}

const CartContext = createContext<CartContextType | undefined>(undefined);

let nextId = 1;

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const isFirstSaveRef = useRef(true);

  useEffect(() => {
    const stored = loadStoredCart();
    if (stored.length > 0) {
      setItems(stored);
      const maxId = Math.max(...stored.map((i) => i.cart_item_id), 0);
      nextId = maxId + 1;
    }
  }, []);

  useEffect(() => {
    if (isFirstSaveRef.current) {
      isFirstSaveRef.current = false;
      return;
    }
    saveCart(items);
  }, [items]);

  const addItem = useCallback(
    (product: Product, aiDecision?: CartItem["ai_decision"], aiReason?: string) => {
      setItems((prev) => {
        const existing = prev.find((i) => i.product.product_id === product.product_id);
        if (existing) {
          return prev.map((i) =>
            i.product.product_id === product.product_id
              ? { ...i, quantity: i.quantity + 1, ai_decision: aiDecision ?? i.ai_decision, ai_reason: aiReason ?? i.ai_reason }
              : i,
          );
        }
        return [
          ...prev,
          {
            cart_item_id: nextId++,
            product,
            quantity: 1,
            checked: true,
            ai_decision: aiDecision,
            ai_reason: aiReason,
          },
        ];
      });
    },
    [],
  );

  const removeItem = useCallback((cartItemId: number) => {
    setItems((prev) => prev.filter((i) => i.cart_item_id !== cartItemId));
  }, []);

  const updateQuantity = useCallback((cartItemId: number, quantity: number) => {
    if (quantity < 1) return;
    setItems((prev) =>
      prev.map((i) => (i.cart_item_id === cartItemId ? { ...i, quantity } : i)),
    );
  }, []);

  const toggleCheck = useCallback((cartItemId: number) => {
    setItems((prev) =>
      prev.map((i) =>
        i.cart_item_id === cartItemId ? { ...i, checked: !i.checked } : i,
      ),
    );
  }, []);

  const toggleCheckAll = useCallback((checked: boolean) => {
    setItems((prev) => prev.map((i) => ({ ...i, checked })));
  }, []);

  const removeChecked = useCallback(() => {
    setItems((prev) => prev.filter((i) => !i.checked));
  }, []);

  const totalCount = items.reduce((sum, i) => sum + i.quantity, 0);

  const checkedItems = useMemo(() => items.filter((i) => i.checked), [items]);

  const productTotal = useMemo(
    () => checkedItems.reduce((sum, i) => sum + i.product.original_price * i.quantity, 0),
    [checkedItems],
  );

  const discountTotal = useMemo(
    () =>
      checkedItems.reduce(
        (sum, i) => sum + (i.product.original_price - i.product.price) * i.quantity,
        0,
      ),
    [checkedItems],
  );

  const deliveryFee = useMemo(() => {
    const subtotal = productTotal - discountTotal;
    return subtotal >= 20000 || subtotal === 0 ? 0 : 3000;
  }, [productTotal, discountTotal]);

  const finalTotal = productTotal - discountTotal + deliveryFee;

  return (
    <CartContext.Provider
      value={{
        items,
        addItem,
        removeItem,
        updateQuantity,
        toggleCheck,
        toggleCheckAll,
        removeChecked,
        totalCount,
        checkedItems,
        productTotal,
        discountTotal,
        finalTotal,
        deliveryFee,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) throw new Error("useCart must be used within CartProvider");
  return context;
}
