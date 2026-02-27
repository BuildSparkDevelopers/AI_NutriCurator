"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, ShieldCheck, AlertTriangle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { getProductById } from "@/lib/mock-data";

interface AIMessagePanelProps {
  productId: number;
  productName: string;
}

type AnalysisStatus = "idle" | "loading" | "done";
type Decision = "safe" | "caution" | "warning";

/** 추천 상품: [이미지URL, 상품명, 키워드?, 상품ID?] */
export type AlternativeItem = [string, string, string?, number?];

interface AnalysisResult {
  decision: Decision;
  reason_summary: string;
  alternatives: AlternativeItem[];
}

const decisionConfig: Record<Decision, { icon: typeof ShieldCheck; color: string; bg: string; border: string; label: string }> = {
  safe: {
    icon: ShieldCheck,
    color: "text-safe-green",
    bg: "bg-green-50",
    border: "border-green-200",
    label: "안전",
  },
  caution: {
    icon: AlertTriangle,
    color: "text-caution-yellow",
    bg: "bg-yellow-50",
    border: "border-yellow-200",
    label: "주의",
  },
  warning: {
    icon: XCircle,
    color: "text-warn-red",
    bg: "bg-red-50",
    border: "border-red-200",
    label: "경고",
  },
};

export default function AIMessagePanel({ productId, productName }: AIMessagePanelProps) {
  const { isLoggedIn, token, logout } = useAuth();
  const [status, setStatus] = useState<AnalysisStatus>("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [expanded, setExpanded] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!isLoggedIn || !token) {
      window.location.href = "/login";
      return;
    }

    setStatus("loading");
    setError(null);

    try {
      // 백엔드 API 호출
      const response = await fetch("/api/v1/ai/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        },
        body: JSON.stringify({
          product_id: productId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 401) {
          logout();
          throw new Error("로그인 세션이 만료되었습니다. 다시 로그인해주세요.");
        }
        throw new Error(errorData.detail || "분석 중 오류가 발생했습니다");
      }

      const data = await response.json();
      const rawAlts = data.alternatives || [];

      // API 응답을 [이미지, 상품명, 키워드?, 상품ID?][] 형식으로 변환
      const alternatives: AlternativeItem[] = rawAlts.map((alt: { product_id?: number; id?: number; name?: string; reason?: string; image_url?: string }) => {
        const pid = alt.product_id ?? alt.id;
        const name = alt.name ?? "";
        const keywords = alt.reason ?? "";
        const product = pid ? getProductById(Number(pid)) : null;
        const image = alt.image_url ?? product?.image_url ?? "https://picsum.photos/seed/placeholder/400/400";
        return [image, name || product?.name || "상품", keywords || undefined, pid ? Number(pid) : undefined];
      });

      setResult({
        decision: data.decision || "safe",
        reason_summary: data.reason_summary || "분석이 완료되었습니다",
        alternatives,
      });
      setStatus("done");
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "분석 중 오류가 발생했습니다";
      setError(errorMessage);
      setStatus("idle");
      console.error("분석 오류:", err);
    }
  };

  if (status === "idle") {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="border border-primary/30 bg-primary-light rounded-xl p-5"
      >
        <div className="flex items-center gap-3 mb-3">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-600">AI 건강 분석</p>
            <p className="text-xs text-gray-400">
              내 건강 프로필 기반으로 이 상품을 분석합니다
            </p>
          </div>
        </div>
        {error && (
          <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-xs text-red-600">{error}</p>
          </div>
        )}
        <button
          onClick={handleAnalyze}
          className="w-full py-3 bg-primary text-white font-medium text-sm rounded-lg hover:bg-primary-dark transition-colors"
        >
          {isLoggedIn ? "🔍 AI 분석 시작하기" : "🔐 로그인 후 분석하기"}
        </button>
      </motion.div>
    );
  }

  if (status === "loading") {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="border border-primary/30 bg-primary-light rounded-xl p-5"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center animate-pulse">
            <Bot size={20} className="text-white" />
          </div>
          <div>
            <p className="text-sm font-bold text-gray-600">AI가 분석 중입니다...</p>
            <p className="text-xs text-gray-400">
              건강 프로필과 상품 영양 성분을 비교하고 있어요
            </p>
          </div>
        </div>
        <div className="mt-4 flex gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-2 h-2 bg-primary rounded-full"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{
                repeat: Infinity,
                duration: 0.8,
                delay: i * 0.2,
              }}
            />
          ))}
        </div>
      </motion.div>
    );
  }

  if (!result) return null;

  const config = decisionConfig[result.decision];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border ${config.border} ${config.bg} rounded-xl overflow-hidden`}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-5 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-full flex items-center justify-center ${
              result.decision === "safe"
                ? "bg-green-100"
                : result.decision === "caution"
                  ? "bg-yellow-100"
                  : "bg-red-100"
            }`}
          >
            <Icon size={20} className={config.color} />
          </div>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className={`text-sm font-bold ${config.color}`}>
                AI 분석 결과: {config.label}
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">
              {productName} 분석 완료
            </p>
          </div>
        </div>
        {expanded ? (
          <ChevronUp size={18} className="text-gray-400" />
        ) : (
          <ChevronDown size={18} className="text-gray-400" />
        )}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-5 space-y-4">
              <p className="text-sm text-gray-600 leading-relaxed">
                {result.reason_summary}
              </p>

              {result.alternatives.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-3">
                    🔄 AI 추천 대체 상품
                  </p>
                  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 sm:gap-4">
                    {result.alternatives.map(([image, name, keywords, productId], idx) => {
                      const content = (
                        <>
                          <div className="relative aspect-square rounded-lg overflow-hidden bg-gray-100">
                            <Image
                              src={image}
                              alt={name}
                              fill
                              className="object-cover"
                              sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
                              unoptimized
                            />
                          </div>
                          <p className="text-xs font-medium text-gray-600 mt-1.5 line-clamp-2">
                            {name}
                          </p>
                          {keywords && (
                            <p className="text-[10px] text-gray-400 mt-0.5 line-clamp-2">
                              {keywords}
                            </p>
                          )}
                        </>
                      );
                      const wrapperClass = "block p-2 sm:p-3 bg-white rounded-xl border border-gray-200 hover:border-primary/40 transition-colors text-left group";
                      return productId ? (
                        <Link
                          key={`${productId}-${idx}`}
                          href={`/products/${productId}`}
                          className={wrapperClass}
                        >
                          {content}
                          <span className="text-[10px] text-primary mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            보기 →
                          </span>
                        </Link>
                      ) : (
                        <div key={idx} className={wrapperClass}>
                          {content}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              <button
                onClick={handleAnalyze}
                className="text-xs text-gray-400 hover:text-primary transition-colors"
              >
                다시 분석하기
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
