"use client";

import { useEffect, useState } from "react";
import CategoryNav from "@/components/CategoryNav";
import ProductCard from "@/components/ProductCard";
import { Product } from "@/lib/types";
import { fetchProducts } from "@/lib/products-api";

export default function ProductsPage() {
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;

    async function loadProducts() {
      setIsLoading(true);
      setError(null);
      try {
        const { items } = await fetchProducts({
          categoryId: selectedCategory,
          limit: 60,
          offset: 0,
        });
        if (!isCancelled) setProducts(items);
      } catch (err) {
        if (!isCancelled) {
          const message =
            err instanceof Error ? err.message : "상품을 불러오는 중 오류가 발생했습니다.";
          setError(message);
          setProducts([]);
        }
      } finally {
        if (!isCancelled) setIsLoading(false);
      }
    }

    loadProducts();
    return () => {
      isCancelled = true;
    };
  }, [selectedCategory]);

  return (
    <div className="mx-auto max-w-[1050px] px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-700 mb-2">전체 상품</h1>
      <p className="text-sm text-gray-400 mb-6">
        카테고리를 선택해서 원하는 상품을 빠르게 찾아보세요.
      </p>

      <CategoryNav
        selectedCategory={selectedCategory}
        onSelect={setSelectedCategory}
      />

      {isLoading ? (
        <div className="py-16 text-center text-gray-400">상품을 불러오는 중입니다...</div>
      ) : error ? (
        <div className="py-16 text-center text-warn-red">{error}</div>
      ) : products.length === 0 ? (
        <div className="py-16 text-center text-gray-400">
          선택한 카테고리의 상품이 없습니다.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6">
          {products.map((product, index) => (
            <ProductCard key={product.product_id} product={product} index={index} />
          ))}
        </div>
      )}
    </div>
  );
}