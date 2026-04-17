"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/use-auth";
import { API_CONFIG } from "@/lib/api/config";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // 이미 로그인된 경우 리다이렉트
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.replace("/briefings/today");
    }
  }, [isAuthenticated, isLoading, router]);

  // 클라이언트 사이드 유효성 검사
  function validate(): string | null {
    if (!email.trim()) return "이메일을 입력해 주세요.";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return "올바른 이메일 형식이 아닙니다.";
    if (!password) return "비밀번호를 입력해 주세요.";
    return null;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setSubmitting(true);
    try {
      await login({ email: email.trim(), password });
      router.replace("/briefings/today");
    } catch (err) {
      setError((err as Error).message || "로그인에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  // Mock 모드 안내
  if (API_CONFIG.USE_MOCK) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-full max-w-sm text-center space-y-4">
          <div className="text-4xl">🔒</div>
          <h1 className="text-xl font-bold text-gray-900">로그인 사용 불가</h1>
          <p className="text-sm text-gray-500">
            현재 Mock 모드로 실행 중입니다.
            <br />
            로그인 기능은 실제 API 모드에서만 사용할 수 있습니다.
          </p>
          <p className="text-xs text-amber-600 bg-amber-50 rounded-lg px-4 py-3">
            <code>NEXT_PUBLIC_USE_MOCK=false</code> 로 변경 후 재시작하세요.
          </p>
          <Link href="/" className="inline-block text-sm text-blue-600 hover:underline">
            홈으로 돌아가기
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="w-full max-w-sm">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">로그인</h1>
          <p className="mt-1.5 text-sm text-gray-500">JobPilot에 오신 것을 환영합니다</p>
        </div>

        {/* 폼 */}
        <form onSubmit={handleSubmit} className="space-y-4" noValidate>
          {/* 이메일 */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              이메일
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              disabled={submitting}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                disabled:bg-gray-50 disabled:text-gray-400 transition-colors"
            />
          </div>

          {/* 비밀번호 */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              비밀번호
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="비밀번호를 입력하세요"
              disabled={submitting}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-lg text-sm
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                disabled:bg-gray-50 disabled:text-gray-400 transition-colors"
            />
          </div>

          {/* 에러 메시지 */}
          {error && (
            <div className="flex items-start gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-lg">
              <span className="text-red-500 mt-0.5 shrink-0">⚠</span>
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          {/* 로그인 버튼 */}
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300
              text-white text-sm font-semibold rounded-lg transition-colors
              focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {submitting ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                로그인 중…
              </span>
            ) : (
              "로그인"
            )}
          </button>
        </form>

        {/* 회원가입 링크 */}
        <p className="mt-6 text-center text-sm text-gray-500">
          아직 계정이 없으신가요?{" "}
          <Link href="/signup" className="font-medium text-blue-600 hover:text-blue-700 hover:underline">
            회원가입
          </Link>
        </p>
      </div>
    </div>
  );
}
