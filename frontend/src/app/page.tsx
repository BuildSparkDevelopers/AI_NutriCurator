"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import Banner from "@/components/Banner";
import CategoryNav from "@/components/CategoryNav";
import ProductCard from "@/components/ProductCard";
import { products } from "@/lib/mock-data";

export default function MainPage() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const filteredProducts = useMemo(() => {
    if (selectedCategory === null) return products;
    return products.filter((p) => p.category_id === selectedCategory);
  }, [selectedCategory]);

  const recommendedProducts = useMemo(() => {
    return [...products]
      .sort((a, b) => b.discount_rate - a.discount_rate)
      .slice(0, 4);
  }, []);

  return (
    <div className="mx-auto max-w-[1050px] px-4 py-6">
      <Banner />

      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="mb-12"
      >
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-600">
              🔥 지금 가장 인기 있는 할인 상품
            </h2>
            <p className="text-sm text-gray-400 mt-1">
              AI가 추천하는 건강 식품을 특별 할인가에 만나보세요
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          {recommendedProducts.map((product, i) => (
            <ProductCard
              key={product.product_id}
              product={product}
              index={i}
            />
          ))}
        </div>
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="text-xl font-bold text-gray-600 mb-6">
          🛒 카테고리별 상품
        </h2>
        <CategoryNav
          selectedCategory={selectedCategory}
          onSelect={setSelectedCategory}
        />

        {filteredProducts.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <p className="text-lg mb-2">해당 카테고리의 상품이 없습니다</p>
            <p className="text-sm">다른 카테고리를 선택해보세요</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
            {filteredProducts.map((product, i) => (
              <ProductCard
                key={product.product_id}
                product={product}
                index={i}
              />
            ))}
          </div>
        )}
      </motion.section>

      <motion.section
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
        className="mt-16 bg-primary-light rounded-2xl p-8 sm:p-12 text-center"
      >
        <h2 className="text-xl sm:text-2xl font-bold text-gray-600 mb-3">
          건강한 식품 선택, AI에게 맡겨보세요
        </h2>
        <p className="text-sm text-gray-400 mb-6 max-w-md mx-auto leading-relaxed">
          나의 건강 프로필을 등록하면 AI가 상품별 영양 성분을 분석하고
          안전한 식품을 추천해드립니다.
        </p>
        <a
          href="/login"
          className="inline-block px-8 py-3 bg-primary text-white font-medium text-sm rounded-full hover:bg-primary-dark transition-colors"
        >
          시작하기
        </a>
      </motion.section>
    </div>
  );
}
