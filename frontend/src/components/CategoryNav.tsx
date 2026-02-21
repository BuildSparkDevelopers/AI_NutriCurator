"use client";

import { categories } from "@/lib/mock-data";
import { motion } from "framer-motion";

interface CategoryNavProps {
  selectedCategory: number | null;
  onSelect: (id: number | null) => void;
}

const categoryIcons: Record<number, string> = {
  1: "🍱",
  2: "💪",
  3: "🥗",
  4: "🧃",
  5: "🍪",
  6: "🥛",
  7: "💊",
  8: "🧊",
};

export default function CategoryNav({
  selectedCategory,
  onSelect,
}: CategoryNavProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="mb-8"
    >
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
        <button
          onClick={() => onSelect(null)}
          className={`shrink-0 flex flex-col items-center gap-1.5 px-4 py-3 rounded-xl border text-sm transition-all ${
            selectedCategory === null
              ? "border-primary bg-primary-light text-primary font-medium"
              : "border-gray-200 bg-white text-gray-500 hover:border-primary/40"
          }`}
        >
          <span className="text-xl">🏠</span>
          <span className="whitespace-nowrap text-xs">전체</span>
        </button>
        {categories.map((cat) => (
          <button
            key={cat.category_id}
            onClick={() => onSelect(cat.category_id)}
            className={`shrink-0 flex flex-col items-center gap-1.5 px-4 py-3 rounded-xl border text-sm transition-all ${
              selectedCategory === cat.category_id
                ? "border-primary bg-primary-light text-primary font-medium"
                : "border-gray-200 bg-white text-gray-500 hover:border-primary/40"
            }`}
          >
            <span className="text-xl">
              {categoryIcons[cat.category_id] || "📦"}
            </span>
            <span className="whitespace-nowrap text-xs">{cat.name}</span>
          </button>
        ))}
      </div>
    </motion.div>
  );
}
