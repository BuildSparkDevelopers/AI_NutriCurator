"use client";

import { useEffect, useMemo, useState } from "react";

export default function MainPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/v1/products");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();

        // ✅ 너희 API 스키마에 맞는 정답
        setProducts(Array.isArray(data?.items) ? data.items : []);
      } catch (e) {
        console.error(e);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const recommendedProducts = useMemo(() => {
    return [...products]
      .sort((a, b) => (b.discount_rate ?? 0) - (a.discount_rate ?? 0))
      .slice(0, 4);
  }, [products]);

  if (loading) return <div className="p-6 text-gray-400">로딩중...</div>;

  // ✅ 비었을 때 안내 UI (지금 같은 상황에서 필수)
  if (products.length === 0) {
    return <div className="p-6 text-gray-400">상품 데이터가 없습니다. DB seed/복구가 필요합니다.</div>;
  }

  return <div>{/* ...기존 렌더... */}</div>;
}