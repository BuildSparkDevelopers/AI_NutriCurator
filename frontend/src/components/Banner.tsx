"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight } from "lucide-react";

const banners = [
  {
    id: 1,
    title: "AI가 분석하는\n나만의 건강 맞춤 식품",
    subtitle: "건강 프로필 기반 식품 추천 서비스",
    bg: "from-primary to-emerald-700",
  },
  {
    id: 2,
    title: "고혈압·당뇨 걱정 없이\n안심하고 드세요",
    subtitle: "질환별 영양 분석으로 안전한 선택",
    bg: "from-teal-600 to-cyan-700",
  },
  {
    id: 3,
    title: "저염·저당 식품\n최대 30% 할인",
    subtitle: "건강한 식단, 합리적인 가격으로",
    bg: "from-emerald-600 to-green-800",
  },
];

export default function Banner() {
  const [current, setCurrent] = useState(0);

  const next = useCallback(
    () => setCurrent((prev) => (prev + 1) % banners.length),
    [],
  );
  const prev = useCallback(
    () => setCurrent((prev) => (prev - 1 + banners.length) % banners.length),
    [],
  );

  useEffect(() => {
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [next]);

  return (
    <div className="relative w-full h-[320px] sm:h-[380px] overflow-hidden rounded-2xl mb-10">
      <AnimatePresence mode="wait">
        <motion.div
          key={banners[current].id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.5 }}
          className={`absolute inset-0 bg-gradient-to-br ${banners[current].bg} flex items-center`}
        >
          <div className="px-8 sm:px-16">
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2, duration: 0.5 }}
              className="text-2xl sm:text-4xl font-bold text-white leading-tight whitespace-pre-line"
            >
              {banners[current].title}
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              className="mt-4 text-white/80 text-sm sm:text-base"
            >
              {banners[current].subtitle}
            </motion.p>
            <motion.button
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.5 }}
              className="mt-6 px-6 py-2.5 bg-white text-primary font-medium text-sm rounded-full hover:bg-gray-100 transition-colors"
            >
              자세히 보기
            </motion.button>
          </div>
        </motion.div>
      </AnimatePresence>

      <button
        onClick={prev}
        className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/40 transition-colors"
      >
        <ChevronLeft size={20} />
      </button>
      <button
        onClick={next}
        className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center text-white hover:bg-white/40 transition-colors"
      >
        <ChevronRight size={20} />
      </button>

      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
        {banners.map((_, i) => (
          <button
            key={i}
            onClick={() => setCurrent(i)}
            className={`w-2 h-2 rounded-full transition-all ${
              i === current ? "w-6 bg-white" : "bg-white/40"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
