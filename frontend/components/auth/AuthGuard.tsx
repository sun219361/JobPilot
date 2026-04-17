"use client";

/**
 * AuthGuard.tsx
 *
 * 인증이 필요한 페이지를 보호하는 컴포넌트.
 *
 * 동작:
 *  - authState === "loading"         → 스켈레톤 표시 (초기 복원 대기)
 *  - authState === "unauthenticated" → /login 으로 리다이렉트
 *  - authState === "authenticated"   → children 렌더링
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
  /** 로그인 후 돌아올 경로 (기본: 현재 경로) */
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

  // 초기 복원 중: 스켈레톤 표시
  if (authState === "loading") {
    return <AuthLoadingSkeleton />;
  }

  // 미로그인: 리다이렉트 트리거 후 빈 화면 (깜빡임 방지)
  if (authState === "unauthenticated") {
    return null;
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
