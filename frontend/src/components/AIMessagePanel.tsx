"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bot, ShieldCheck, AlertTriangle, XCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

interface AIMessagePanelProps {
  productId: number;
  productName: string;
}

type AnalysisStatus = "idle" | "loading" | "done";
type Decision = "safe" | "caution" | "warning";

interface AnalysisResult {
  decision: Decision;
  reason_summary: string;
  alternatives: { id: number; name: string }[];
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
  const { isLoggedIn } = useAuth();
  const [status, setStatus] = useState<AnalysisStatus>("idle");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [expanded, setExpanded] = useState(true);

  const handleAnalyze = async () => {
    if (!isLoggedIn) {
      window.location.href = "/login";
      return;
    }

    setStatus("loading");
    await new Promise((r) => setTimeout(r, 2000));

    setResult({
      decision: "caution",
      reason_summary: `고혈압 전단계 사용자로 "${productName}"의 나트륨 함량(420mg)이 일일 권장 섭취량 대비 높은 편입니다. 저염 대체 상품을 확인해보세요.`,
      alternatives: [
        { id: 10046, name: "저염 김치찌개" },
        { id: 10049, name: "퀴노아 현미 밥" },
        { id: 10048, name: "곤약 젤리 복숭아" },
      ],
    });
    setStatus("done");
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
                  <p className="text-xs font-medium text-gray-500 mb-2">
                    🔄 AI 추천 대체 상품
                  </p>
                  <div className="space-y-2">
                    {result.alternatives.map((alt) => (
                      <a
                        key={alt.id}
                        href={`/products/${alt.id}`}
                        className="flex items-center gap-2 px-3 py-2 bg-white rounded-lg border border-gray-200 hover:border-primary/40 transition-colors text-sm text-gray-600 hover:text-primary"
                      >
                        <ShieldCheck size={14} className="text-safe-green shrink-0" />
                        {alt.name}
                        <span className="ml-auto text-xs text-primary">보기 →</span>
                      </a>
                    ))}
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
