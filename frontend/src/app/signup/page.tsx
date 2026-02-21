"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

const DIABETES_OPTIONS = [
  { value: "", label: "해당없음" },
  { value: "1형", label: "1형" },
  { value: "2형", label: "2형" },
];

const HYPERTENSION_OPTIONS = [
  { value: "", label: "해당없음" },
  { value: "정상", label: "정상" },
  { value: "전단계", label: "전단계" },
  { value: "고혈압", label: "고혈압" },
];

const KIDNEY_OPTIONS = [
  { value: "", label: "해당없음" },
  { value: "CKD3~5", label: "CKD3~5" },
  { value: "혈압투석", label: "혈압투석" },
  { value: "복막투석", label: "복막투석" },
];

const ALLERGY_OPTIONS = [
  "계란 (가금류)",
  "우유",
  "메밀",
  "땅콩",
  "대두 (콩)",
  "밀",
  "고등어",
  "게",
  "새우",
  "돼지고기",
  "복숭아",
  "토마토",
  "아황산류",
  "호두",
  "닭고기",
  "소고기",
  "오징어",
  "조개류 (굴, 전복, 홍합 등 포함)",
  "잣",
];

function SignupForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectUrl = searchParams.get("internalUrl") || "/";
  const { signup } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordConfirm, setPasswordConfirm] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);

  const [diabetes, setDiabetes] = useState("");
  const [hypertension, setHypertension] = useState("");
  const [kidneydisease, setKidneydisease] = useState("");
  const [allergy, setAllergy] = useState<string[]>([]);

  const [tosAgreed, setTosAgreed] = useState(false);
  const [privacyAgreed, setPrivacyAgreed] = useState(false);
  const [sensitiveAgreed, setSensitiveAgreed] = useState(false);

  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const hasHealthInfo =
    diabetes || hypertension || kidneydisease || allergy.length > 0;

  const toggleAllergy = (item: string) => {
    setAllergy((prev) =>
      prev.includes(item) ? prev.filter((a) => a !== item) : [...prev, item],
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email) {
      setError("이메일을 입력해주세요.");
      return;
    }
    if (!password) {
      setError("비밀번호를 입력해주세요.");
      return;
    }
    if (password.length < 8) {
      setError("비밀번호는 8자 이상이어야 합니다.");
      return;
    }
    if (password !== passwordConfirm) {
      setError("비밀번호가 일치하지 않습니다.");
      return;
    }
    if (!tosAgreed || !privacyAgreed) {
      setError("필수 이용약관에 동의해주세요.");
      return;
    }
    if (hasHealthInfo && !sensitiveAgreed) {
      setError(
        "건강정보를 입력하신 경우, 민감정보 수집 동의에 체크해주세요.",
      );
      return;
    }

    setIsLoading(true);
    await new Promise((r) => setTimeout(r, 500));
    const success = await signup(email, password, {
      diabetes: diabetes || undefined,
      hypertension: hypertension || undefined,
      kidneydisease: kidneydisease || undefined,
      allergy: allergy.length > 0 ? allergy : undefined,
    });
    setIsLoading(false);

    if (success) {
      router.push(redirectUrl);
    } else {
      setError("회원가입 처리 중 오류가 발생했습니다.");
    }
  };

  return (
    <div className="min-h-[70vh] flex items-center justify-center px-4 py-12">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-[480px]"
      >
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white font-bold text-xl">N</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-600">회원가입</h1>
          <p className="text-sm text-gray-400 mt-2">
            NutriCurator와 함께 건강한 식품을 선택하세요
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* 필수 입력 */}
          <div>
            <h2 className="text-sm font-bold text-gray-600 mb-3">필수 입력</h2>
            <div className="space-y-3">
              <div className="relative">
                <Mail
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-300"
                />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="이메일"
                  className="w-full h-12 pl-11 pr-4 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-colors"
                />
              </div>
              <div className="relative">
                <Lock
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-300"
                />
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="비밀번호 (8자 이상)"
                  className="w-full h-12 pl-11 pr-11 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500"
                >
                  {showPassword ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
              <div className="relative">
                <Lock
                  size={18}
                  className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-300"
                />
                <input
                  type={showPasswordConfirm ? "text" : "password"}
                  value={passwordConfirm}
                  onChange={(e) => setPasswordConfirm(e.target.value)}
                  placeholder="비밀번호 확인"
                  className="w-full h-12 pl-11 pr-11 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 transition-colors"
                />
                <button
                  type="button"
                  onClick={() =>
                    setShowPasswordConfirm(!showPasswordConfirm)
                  }
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-300 hover:text-gray-500"
                >
                  {showPasswordConfirm ? (
                    <EyeOff size={18} />
                  ) : (
                    <Eye size={18} />
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* 건강정보 (비필수) */}
          <div>
            <h2 className="text-sm font-bold text-gray-600 mb-2">
              건강정보{" "}
              <span className="text-gray-400 font-normal text-xs">
                (선택)
              </span>
            </h2>
            <p className="text-xs text-gray-500 mb-4 leading-relaxed">
              입력시 고객님의 건강정보에 적합한 식품 추천 혜택을 받아보실 수
              있습니다.
            </p>

            <div className="space-y-4">
              <div>
                <label className="block text-xs text-gray-500 mb-1.5">
                  당뇨병
                </label>
                <select
                  value={diabetes}
                  onChange={(e) => setDiabetes(e.target.value)}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 bg-white"
                >
                  {DIABETES_OPTIONS.map((opt) => (
                    <option key={opt.value || "none"} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-1.5">
                  고혈압
                </label>
                <select
                  value={hypertension}
                  onChange={(e) => setHypertension(e.target.value)}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 bg-white"
                >
                  {HYPERTENSION_OPTIONS.map((opt) => (
                    <option key={opt.value || "none"} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-1.5">
                  신장이상
                </label>
                <select
                  value={kidneydisease}
                  onChange={(e) => setKidneydisease(e.target.value)}
                  className="w-full h-10 px-3 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/30 bg-white"
                >
                  {KIDNEY_OPTIONS.map((opt) => (
                    <option key={opt.value || "none"} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-2">
                  알레르기
                </label>
                <div className="border border-gray-200 rounded-lg p-3 max-h-40 overflow-y-auto bg-gray-50/50">
                  <div className="grid grid-cols-2 gap-2">
                    {ALLERGY_OPTIONS.map((item) => (
                      <label
                        key={item}
                        className="flex items-center gap-2 cursor-pointer text-sm text-gray-600 hover:text-primary transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={allergy.includes(item)}
                          onChange={() => toggleAllergy(item)}
                          className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
                        />
                        <span className="truncate">{item}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 이용약관 동의 */}
          <div>
            <h2 className="text-sm font-bold text-gray-600 mb-3">
              이용약관 동의
            </h2>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={tosAgreed}
                  onChange={(e) => setTosAgreed(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
                />
                <span className="text-sm text-gray-600">
                  이용약관 동의
                  <span className="text-warn-red"> (필수)</span>
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={privacyAgreed}
                  onChange={(e) => setPrivacyAgreed(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
                />
                <span className="text-sm text-gray-600">
                  개인정보 수집 및 이용 동의
                  <span className="text-warn-red"> (필수)</span>
                </span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={sensitiveAgreed}
                  onChange={(e) => setSensitiveAgreed(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-300 text-primary focus:ring-primary accent-primary"
                />
                <span className="text-sm text-gray-600">
                  민감정보 수집 동의
                  <span className="text-gray-400"> (선택)</span>
                </span>
              </label>
              {hasHealthInfo && !sensitiveAgreed && (
                <p className="text-xs text-warn-red mt-1 ml-6">
                  건강정보를 입력하신 경우 민감정보 수집 동의에 체크해주세요.
                </p>
              )}
            </div>
          </div>

          {error && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-xs text-warn-red"
            >
              {error}
            </motion.p>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full h-12 bg-primary text-white font-medium text-sm rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? "가입 처리 중..." : "가입하기"}
          </button>
        </form>

        <div className="mt-6 text-center">
          <span className="text-sm text-gray-400">이미 회원이신가요? </span>
          <Link
            href={`/login${redirectUrl !== "/" ? `?internalUrl=${encodeURIComponent(redirectUrl)}` : ""}`}
            className="text-sm text-primary font-medium hover:underline"
          >
            로그인
          </Link>
        </div>
      </motion.div>
    </div>
  );
}

export default function SignupPage() {
  return (
    <Suspense fallback={<div className="min-h-[70vh] flex items-center justify-center">로딩 중...</div>}>
      <SignupForm />
    </Suspense>
  );
}
