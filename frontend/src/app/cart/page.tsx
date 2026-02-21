"use client";

import { useMemo } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  X,
  Minus,
  Plus,
  ShieldCheck,
  AlertTriangle,
  XCircle,
  Truck,
  ShoppingCart,
  Info,
} from "lucide-react";
import { useCart } from "@/lib/cart-context";
import { useAuth } from "@/lib/auth-context";
import { formatPrice } from "@/lib/mock-data";
import type { CartItem } from "@/lib/types";

const FREE_DELIVERY_THRESHOLD = 20000;

function AIBadge({ decision, reason }: { decision?: CartItem["ai_decision"]; reason?: string }) {
  if (!decision) return null;
  const config = {
    safe: { icon: ShieldCheck, color: "text-safe-green", bg: "bg-green-50", border: "border-green-200", label: "안전" },
    caution: { icon: AlertTriangle, color: "text-caution-yellow", bg: "bg-yellow-50", border: "border-yellow-200", label: "주의" },
    warning: { icon: XCircle, color: "text-warn-red", bg: "bg-red-50", border: "border-red-200", label: "경고" },
  }[decision];
  const Icon = config.icon;
  return (
    <div className={`flex items-start gap-2 mt-2 px-3 py-2 rounded-lg text-xs ${config.bg} border ${config.border}`}>
      <Icon size={14} className={`${config.color} shrink-0 mt-0.5`} />
      <div>
        <span className={`font-medium ${config.color}`}>AI 분석: {config.label}</span>
        {reason && <p className="text-gray-500 mt-0.5 leading-relaxed">{reason}</p>}
      </div>
    </div>
  );
}

export default function CartPage() {
  const { isLoggedIn } = useAuth();
  const {
    items,
    removeItem,
    updateQuantity,
    toggleCheck,
    toggleCheckAll,
    removeChecked,
    checkedItems,
    productTotal,
    discountTotal,
    finalTotal,
    deliveryFee,
  } = useCart();

  const allChecked = useMemo(
    () => items.length > 0 && items.every((i) => i.checked),
    [items],
  );

  const remainForFree = useMemo(() => {
    const subtotal = productTotal - discountTotal;
    return subtotal >= FREE_DELIVERY_THRESHOLD ? 0 : FREE_DELIVERY_THRESHOLD - subtotal;
  }, [productTotal, discountTotal]);

  if (!isLoggedIn) {
    return (
      <div className="mx-auto max-w-[1050px] px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <ShoppingCart size={64} className="mx-auto text-gray-200 mb-6" />
          <h1 className="text-xl font-bold text-gray-600 mb-2">
            로그인이 필요한 서비스입니다
          </h1>
          <p className="text-sm text-gray-400 mb-6">
            장바구니를 이용하려면 먼저 로그인해주세요.
          </p>
          <Link
            href="/login"
            className="inline-block px-8 py-3 bg-primary text-white font-medium text-sm rounded-lg hover:bg-primary-dark transition-colors"
          >
            로그인하기
          </Link>
        </motion.div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="mx-auto max-w-[1050px] px-4 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <ShoppingCart size={64} className="mx-auto text-gray-200 mb-6" />
          <h1 className="text-xl font-bold text-gray-600 mb-2">
            장바구니에 담긴 상품이 없습니다
          </h1>
          <p className="text-sm text-gray-400 mb-6">
            AI 건강 분석 후 맞춤 상품을 담아보세요.
          </p>
          <Link
            href="/"
            className="inline-block px-8 py-3 bg-primary text-white font-medium text-sm rounded-lg hover:bg-primary-dark transition-colors"
          >
            쇼핑 계속하기
          </Link>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-[1050px] px-4 py-8">
      {/* Page title */}
      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-2xl font-bold text-gray-600 text-center mb-2"
      >
        장바구니
      </motion.h1>

      {/* Free delivery banner */}
      {remainForFree > 0 && checkedItems.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center gap-2 py-2.5 bg-primary-light rounded-lg text-sm text-primary"
        >
          <Truck size={16} />
          <span>
            <strong>{formatPrice(remainForFree)}원</strong> 더 담으면{" "}
            <strong>무료배송</strong>
          </span>
        </motion.div>
      )}
      {remainForFree === 0 && checkedItems.length > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 flex items-center justify-center gap-2 py-2.5 bg-primary-light rounded-lg text-sm text-primary font-medium"
        >
          <Truck size={16} />
          무료배송 대상입니다
        </motion.div>
      )}

      <div className="mt-8 flex flex-col lg:flex-row gap-6">
        {/* Left: Cart items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="flex-1 min-w-0"
        >
          {/* Select all / Delete */}
          <div className="flex items-center justify-between py-4 border-b border-gray-600">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={allChecked}
                onChange={(e) => toggleCheckAll(e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
              />
              <span className="text-sm text-gray-600">
                전체선택 ({checkedItems.length}/{items.length})
              </span>
            </label>
            <button
              onClick={removeChecked}
              className="text-sm text-gray-400 border border-gray-200 px-3 py-1.5 rounded hover:bg-gray-50 transition-colors"
            >
              선택삭제
            </button>
          </div>

          {/* Delivery group title */}
          <div className="flex items-center gap-2 py-4 border-b border-kurly-border">
            <div className="w-1.5 h-1.5 bg-primary rounded-full" />
            <span className="text-sm font-bold text-gray-600">샛별배송</span>
            <span className="text-xs text-gray-400">23시 전 주문 시 내일 아침 7시 전 도착</span>
          </div>

          {/* Cart items */}
          <ul>
            {items.map((item, idx) => (
              <motion.li
                key={item.cart_item_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="flex gap-4 py-5 border-b border-kurly-border"
              >
                {/* Checkbox */}
                <div className="flex items-start pt-1">
                  <input
                    type="checkbox"
                    checked={item.checked}
                    onChange={() => toggleCheck(item.cart_item_id)}
                    className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
                  />
                </div>

                {/* Product image */}
                <Link
                  href={`/products/${item.product.product_id}`}
                  className="shrink-0 w-[60px] h-[78px] sm:w-[60px] sm:h-[78px] relative rounded overflow-hidden bg-gray-100"
                >
                  <Image
                    src={item.product.image_url}
                    alt={item.product.name}
                    fill
                    className="object-cover"
                    sizes="60px"
                  />
                </Link>

                {/* Product info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <Link
                        href={`/products/${item.product.product_id}`}
                        className="text-sm text-gray-600 hover:text-primary transition-colors line-clamp-2"
                      >
                        [{item.product.brand}] {item.product.name}
                      </Link>
                    </div>
                    <button
                      onClick={() => removeItem(item.cart_item_id)}
                      className="shrink-0 p-1 text-gray-300 hover:text-gray-500 transition-colors"
                    >
                      <X size={18} />
                    </button>
                  </div>

                  {/* AI badge */}
                  <AIBadge decision={item.ai_decision} reason={item.ai_reason} />

                  {/* Quantity + Price row */}
                  <div className="flex items-center justify-between mt-3">
                    {/* Quantity controls */}
                    <div className="flex items-center border border-gray-200 rounded">
                      <button
                        onClick={() => updateQuantity(item.cart_item_id, item.quantity - 1)}
                        disabled={item.quantity <= 1}
                        className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 disabled:opacity-30 transition-colors"
                      >
                        <Minus size={14} />
                      </button>
                      <span className="w-9 text-center text-sm text-gray-600 font-medium">
                        {item.quantity}
                      </span>
                      <button
                        onClick={() => updateQuantity(item.cart_item_id, item.quantity + 1)}
                        className="w-8 h-8 flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <Plus size={14} />
                      </button>
                    </div>

                    {/* Price */}
                    <div className="text-right">
                      <p className="text-sm font-bold text-gray-600">
                        {formatPrice(item.product.price * item.quantity)}원
                      </p>
                      {item.product.discount_rate > 0 && (
                        <p className="text-xs text-gray-300 line-through">
                          {formatPrice(item.product.original_price * item.quantity)}원
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </motion.li>
            ))}
          </ul>

          {/* Bottom select all */}
          <div className="flex items-center justify-between py-4 border-b border-gray-200">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={allChecked}
                onChange={(e) => toggleCheckAll(e.target.checked)}
                className="w-5 h-5 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
              />
              <span className="text-sm text-gray-600">
                전체선택 ({checkedItems.length}/{items.length})
              </span>
            </label>
            <button
              onClick={removeChecked}
              className="text-sm text-gray-400 border border-gray-200 px-3 py-1.5 rounded hover:bg-gray-50 transition-colors"
            >
              선택삭제
            </button>
          </div>
        </motion.div>

        {/* Right: Order summary (sticky sidebar) */}
        <motion.aside
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="lg:w-[284px] shrink-0"
        >
          <div className="lg:sticky lg:top-[140px]">
            <div className="border border-kurly-border rounded-lg overflow-hidden">
              {/* Delivery info */}
              <div className="bg-gray-100 px-5 py-4">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Truck size={16} className="text-primary" />
                  <span className="font-medium">배송지</span>
                </div>
                <p className="text-xs text-gray-400 mt-1.5 ml-6">
                  서울 강남구 테헤란로 133
                </p>
                <p className="text-[11px] text-primary mt-1 ml-6">
                  샛별배송
                </p>
              </div>

              {/* Price summary */}
              <div className="px-5 py-5 space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">상품금액</span>
                  <span className="text-gray-600 font-medium">
                    {formatPrice(productTotal)}원
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">상품할인금액</span>
                  <span className="text-warn-red font-medium">
                    {discountTotal > 0 ? `-${formatPrice(discountTotal)}` : "0"}원
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">배송비</span>
                  <span className="text-gray-600 font-medium">
                    {deliveryFee === 0 ? (
                      <span className="text-primary">무료</span>
                    ) : (
                      `+${formatPrice(deliveryFee)}원`
                    )}
                  </span>
                </div>
                <div className="border-t border-kurly-border pt-3 flex items-center justify-between">
                  <span className="text-sm font-bold text-gray-600">
                    결제예정금액
                  </span>
                  <span className="text-lg font-bold text-gray-600">
                    {formatPrice(finalTotal)}
                    <span className="text-sm font-normal">원</span>
                  </span>
                </div>
              </div>

              {/* Nutrition summary for checked items */}
              {checkedItems.length > 0 && (
                <div className="border-t border-kurly-border px-5 py-4">
                  <div className="flex items-center gap-1.5 mb-3">
                    <Info size={14} className="text-primary" />
                    <span className="text-xs font-medium text-gray-500">
                      선택 상품 영양 합산
                    </span>
                  </div>
                  <NutritionSummary items={checkedItems} />
                </div>
              )}
            </div>

            {/* Order button */}
            <button
              disabled={checkedItems.length === 0}
              className="w-full mt-4 h-14 bg-primary text-white font-bold text-base rounded-lg hover:bg-primary-dark transition-colors disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {checkedItems.length === 0
                ? "상품을 선택해주세요"
                : `주문하기 (${checkedItems.length}개)`}
            </button>

            <ul className="mt-4 space-y-1.5 text-[11px] text-gray-400 leading-relaxed">
              <li className="flex items-start gap-1">
                <span className="shrink-0">·</span>
                쿠폰/적립금은 주문서에서 사용 가능합니다.
              </li>
              <li className="flex items-start gap-1">
                <span className="shrink-0">·</span>
                [주문완료] 상태일 경우에만 주문 취소 가능합니다.
              </li>
              <li className="flex items-start gap-1">
                <span className="shrink-0">·</span>
                2만원 이상 주문 시 무료배송됩니다.
              </li>
            </ul>
          </div>
        </motion.aside>
      </div>
    </div>
  );
}

function NutritionSummary({ items }: { items: CartItem[] }) {
  const totals = useMemo(() => {
    return items.reduce(
      (acc, item) => {
        const n = item.product.nutrition;
        const q = item.quantity;
        return {
          calories: acc.calories + n.calories_kcal * q,
          protein: acc.protein + n.protein_g * q,
          fat: acc.fat + n.fat_g * q,
          carbs: acc.carbs + n.carbohydrate_g * q,
          sodium: acc.sodium + n.sodium_mg * q,
        };
      },
      { calories: 0, protein: 0, fat: 0, carbs: 0, sodium: 0 },
    );
  }, [items]);

  const rows = [
    { label: "칼로리", value: totals.calories, unit: "kcal" },
    { label: "단백질", value: totals.protein, unit: "g" },
    { label: "지방", value: totals.fat, unit: "g" },
    { label: "탄수화물", value: totals.carbs, unit: "g" },
    { label: "나트륨", value: totals.sodium, unit: "mg" },
  ];

  return (
    <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
      {rows.map((r) => (
        <div key={r.label} className="flex items-center justify-between text-xs">
          <span className="text-gray-400">{r.label}</span>
          <span className="text-gray-600 font-medium">
            {r.value % 1 === 0 ? r.value : r.value.toFixed(1)}
            {r.unit}
          </span>
        </div>
      ))}
    </div>
  );
}
