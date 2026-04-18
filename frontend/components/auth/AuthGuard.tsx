"use client";

/**
 * AuthGuard.tsx
 *
 * 인증이 필요한 페이지를 보호하는 컴포넌트.
 *
 * 동작:
 *  - authState === "loading"         → 스켈레톤 표시 (초기 복원 대기)
 *  - authState === "unauthenticated" → 스켈레톤 유지하면서 /login 리다이렉트
 *                                      (null 반환 시 빈 화면 깜빡임 방지)
 *  - authState === "authenticated"   → children 렌더링
 *
 * [QA 수정] unauthenticated 상태에서 null 대신 스켈레톤을 유지하고,
 * useEffect에서 리다이렉트를 트리거한다.
 * 이렇게 하면 loading → unauthenticated 전환 시 화면이 깜빡이지 않는다.
 *
 * 사용법:
 *  export default function ProtectedPage() {
 *    return (
 *      <AuthGuard>
 *        <PageContent />
 *      </AuthGuard>
 *    );
 *  }
 */

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/use-auth";

interface AuthGuardProps {
  children: React.ReactNode;
  /** 리다이렉트 목적지 (기본: /login) */
  redirectTo?: string;
}

export function AuthGuard({ children, redirectTo = "/login" }: AuthGuardProps) {
  const { authState } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (authState === "unauthenticated") {
      router.replace(redirectTo);
    }
  }, [authState, redirectTo, router]);

  // loading 중이거나 아직 unauthenticated 리다이렉트가 실행되기 전:
  // 스켈레톤을 표시한다. null을 반환하면 빈 화면이 순간 보여 깜빡임이 생긴다.
  if (authState === "loading" || authState === "unauthenticated") {
    return <AuthLoadingSkeleton />;
  }

  // 로그인 완료: 실제 콘텐츠 렌더링
  return <>{children}</>;
}

// ─────────────────────────────────────────────
// 로딩 스켈레톤
// ─────────────────────────────────────────────

function AuthLoadingSkeleton() {
  return (
    <div className="space-y-4 animate-pulse">
      {/* 페이지 헤더 스켈레톤 */}
      <div className="space-y-2">
        <div className="h-6 w-32 bg-gray-200 rounded" />
        <div className="h-4 w-56 bg-gray-100 rounded" />
      </div>
      {/* 카드 스켈레톤 × 3 */}
      {[0, 1, 2].map((i) => (
        <div key={i} className="h-20 bg-white rounded-xl border border-gray-100" />
      ))}
    </div>
  );
}
