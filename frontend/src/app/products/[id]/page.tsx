"use client";

import { useParams, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  Heart,
  Share2,
  ShoppingCart,
  ChevronRight,
  Truck,
  Clock,
  Star,
  Check,
} from "lucide-react";
import AIMessagePanel from "@/components/AIMessagePanel";
import ProductCard from "@/components/ProductCard";
import { useCart } from "@/lib/cart-context";
import { useAuth } from "@/lib/auth-context";
import { getProductById, getCategoryById, products, formatPrice } from "@/lib/mock-data";

export default function ProductDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { addItem } = useCart();
  const { isLoggedIn } = useAuth();
  const [addedToast, setAddedToast] = useState(false);
  const productId = Number(params.id);
  const product = getProductById(productId);

  const handleAddToCart = () => {
    if (!isLoggedIn) {
      router.push("/login");
      return;
    }
    if (!product) return;
    addItem(product, "caution", `고혈압 전단계 사용자로 "${product.name}"의 나트륨 함량이 높은 편입니다.`);
    setAddedToast(true);
    setTimeout(() => setAddedToast(false), 2500);
  };

  const relatedProducts = useMemo(() => {
    if (!product) return [];
    return products
      .filter(
        (p) =>
          p.category_id === product.category_id &&
          p.product_id !== product.product_id,
      )
      .slice(0, 4);
  }, [product]);

  if (!product) {
    return (
      <div className="mx-auto max-w-[1050px] px-4 py-20 text-center">
        <p className="text-lg text-gray-400">상품을 찾을 수 없습니다</p>
        <Link
          href="/"
          className="inline-block mt-4 text-sm text-primary hover:underline"
        >
          메인으로 돌아가기
        </Link>
      </div>
    );
  }

  const category = getCategoryById(product.category_id);
  const { nutrition } = product;

  const nutrientRows = [
    { label: "칼로리", value: nutrition.calories_kcal, unit: "kcal" },
    { label: "단백질", value: nutrition.protein_g, unit: "g" },
    { label: "지방", value: nutrition.fat_g, unit: "g" },
    { label: "탄수화물", value: nutrition.carbohydrate_g, unit: "g" },
    { label: "당류", value: nutrition.sugar_g, unit: "g" },
    { label: "나트륨", value: nutrition.sodium_mg, unit: "mg" },
    { label: "콜레스테롤", value: nutrition.cholesterol_mg, unit: "mg" },
    { label: "포화지방", value: nutrition.saturated_fat_g, unit: "g" },
    { label: "트랜스지방", value: nutrition.trans_fat_g, unit: "g" },
  ];

  return (
    <div className="mx-auto max-w-[1050px] px-4 py-6">
      {/* Breadcrumb */}
      <motion.nav
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="flex items-center gap-1 text-xs text-gray-400 mb-6"
      >
        <Link href="/" className="hover:text-primary">
          홈
        </Link>
        <ChevronRight size={12} />
        <span>{category?.name || "카테고리"}</span>
        <ChevronRight size={12} />
        <span className="text-gray-600">{product.name}</span>
      </motion.nav>

      {/* Product top section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        {/* Image */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5 }}
          className="relative aspect-square rounded-xl overflow-hidden bg-gray-100"
        >
          <Image
            src={product.image_url}
            alt={product.name}
            fill
            className="object-cover"
            priority
            sizes="(max-width: 768px) 100vw, 50vw"
          />
          {product.discount_rate > 0 && (
            <span className="absolute top-4 left-4 bg-warn-red text-white text-sm font-bold px-3 py-1.5 rounded-lg">
              {product.discount_rate}% OFF
            </span>
          )}
        </motion.div>

        {/* Product info */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="mb-4">
            <p className="text-sm text-gray-400 mb-1">{product.brand}</p>
            <h1 className="text-2xl font-bold text-gray-600 leading-tight">
              {product.name}
            </h1>
            <p className="text-sm text-gray-400 mt-2 leading-relaxed">
              {product.description}
            </p>
          </div>

          {/* Rating */}
          <div className="flex items-center gap-2 mb-4">
            <div className="flex">
              {[1, 2, 3, 4, 5].map((s) => (
                <Star
                  key={s}
                  size={14}
                  className={s <= 4 ? "text-yellow-400 fill-yellow-400" : "text-gray-200"}
                />
              ))}
            </div>
            <span className="text-xs text-gray-400">4.2 (128개 후기)</span>
          </div>

          {/* Price */}
          <div className="border-t border-b border-kurly-border py-4 mb-4">
            {product.discount_rate > 0 && (
              <p className="text-sm text-gray-300 line-through mb-1">
                {formatPrice(product.original_price)}원
              </p>
            )}
            <div className="flex items-baseline gap-2">
              {product.discount_rate > 0 && (
                <span className="text-2xl font-bold text-warn-red">
                  {product.discount_rate}%
                </span>
              )}
              <span className="text-2xl font-bold text-gray-600">
                {formatPrice(product.price)}원
              </span>
            </div>
          </div>

          {/* Delivery info */}
          <div className="space-y-3 mb-6">
            <div className="flex items-center gap-3">
              <Truck size={16} className="text-gray-400" />
              <div>
                <span className="text-sm text-gray-600">샛별배송</span>
                <span className="text-xs text-gray-400 ml-2">
                  23시 전 주문 시 내일 아침 7시 전 도착
                </span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Clock size={16} className="text-gray-400" />
              <span className="text-sm text-gray-600">
                판매자: {product.brand}
              </span>
            </div>
          </div>

          {/* AI Analysis Panel - positioned between price info and CTA */}
          <div className="mb-6">
            <AIMessagePanel
              productId={product.product_id}
              productName={product.name}
            />
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 relative">
            <button className="w-12 h-12 border border-gray-200 rounded-lg flex items-center justify-center hover:border-primary/40 transition-colors">
              <Heart size={20} className="text-gray-400" />
            </button>
            <button className="w-12 h-12 border border-gray-200 rounded-lg flex items-center justify-center hover:border-primary/40 transition-colors">
              <Share2 size={20} className="text-gray-400" />
            </button>
            <button
              onClick={handleAddToCart}
              className="flex-1 h-12 bg-primary text-white font-medium text-sm rounded-lg hover:bg-primary-dark transition-colors flex items-center justify-center gap-2"
            >
              <ShoppingCart size={18} />
              분석 담기
            </button>
          </div>

          {/* Added to cart toast */}
          <AnimatePresence>
            {addedToast && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="mt-3 flex items-center justify-between gap-3 px-4 py-3 bg-gray-600 rounded-lg text-white text-sm"
              >
                <div className="flex items-center gap-2">
                  <Check size={16} className="text-primary-light" />
                  장바구니에 담았습니다.
                </div>
                <Link
                  href="/cart"
                  className="shrink-0 text-xs text-primary-light underline hover:text-white transition-colors"
                >
                  장바구니 보기
                </Link>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Nutrition info section */}
      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="border-t border-kurly-border pt-10 mb-12"
      >
        <h2 className="text-lg font-bold text-gray-600 mb-6">
          📊 영양 성분 정보
        </h2>
        <div className="bg-gray-100 rounded-xl p-6">
          <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
            <span className="text-sm font-medium text-gray-500">
              1회 제공량 {nutrition.serving_size}
              {nutrition.food_weight}g
            </span>
            <span className="text-xs text-gray-400">
              GI: {nutrition.gi} / GL: {nutrition.gl}
            </span>
          </div>
          <div className="grid grid-cols-3 gap-4 mb-6">
            {[
              {
                label: "칼로리",
                value: `${nutrition.calories_kcal}kcal`,
                accent: true,
              },
              {
                label: "단백질",
                value: `${nutrition.protein_g}g`,
                accent: false,
              },
              {
                label: "지방",
                value: `${nutrition.fat_g}g`,
                accent: false,
              },
            ].map((item) => (
              <div
                key={item.label}
                className={`text-center p-3 rounded-lg ${item.accent ? "bg-primary-light" : "bg-white"}`}
              >
                <p className="text-xs text-gray-400 mb-1">{item.label}</p>
                <p
                  className={`text-lg font-bold ${item.accent ? "text-primary" : "text-gray-600"}`}
                >
                  {item.value}
                </p>
              </div>
            ))}
          </div>
          <table className="w-full text-sm">
            <tbody>
              {nutrientRows.map((row, i) => (
                <tr
                  key={row.label}
                  className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
                >
                  <td className="px-4 py-2.5 text-gray-500">{row.label}</td>
                  <td className="px-4 py-2.5 text-right font-medium text-gray-600">
                    {row.value}
                    {row.unit}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Raw materials */}
        <div className="mt-6 space-y-4">
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">
              원재료명
            </h3>
            <p className="text-sm text-gray-400 bg-gray-50 p-4 rounded-lg">
              {nutrition.rawmtrl}
            </p>
          </div>
          {nutrition.allergymtrl && (
            <div>
              <h3 className="text-sm font-medium text-gray-500 mb-2">
                ⚠️ 알레르기 유발 성분
              </h3>
              <p className="text-sm text-warn-red bg-red-50 p-4 rounded-lg font-medium">
                {nutrition.allergymtrl}
              </p>
            </div>
          )}
        </div>
      </motion.section>

      {/* Related products */}
      {relatedProducts.length > 0 && (
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="border-t border-kurly-border pt-10"
        >
          <h2 className="text-lg font-bold text-gray-600 mb-6">
            🛒 같은 카테고리 상품
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            {relatedProducts.map((p, i) => (
              <ProductCard key={p.product_id} product={p} index={i} />
            ))}
          </div>
        </motion.section>
      )}
    </div>
  );
}
