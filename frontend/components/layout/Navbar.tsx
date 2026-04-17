"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth/use-auth";
import { API_CONFIG } from "@/lib/api/config";

const NAV_ITEMS = [
  { href: "/briefings/today", label: "오늘 브리핑", icon: "📋" },
  { href: "/subscriptions", label: "관심기업", icon: "⭐" },
];

export function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { isAuthenticated, isLoading, user, logout } = useAuth();

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="max-w-2xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* 로고 */}
        <Link href="/" className="flex items-center gap-1.5 shrink-0">
          <span className="text-base font-bold text-gray-900">JobPilot</span>
          <span className="text-xs text-gray-400 hidden sm:inline">관심기업 브리핑</span>
        </Link>

        {/* 오른쪽 영역 */}
        <div className="flex items-center gap-1">
          {/* 네비 링크 (로그인 상태일 때만) */}
          {isAuthenticated && (
            <nav className="flex items-center gap-1 mr-2">
              {NAV_ITEMS.map((item) => {
                const isActive =
                  pathname === item.href || pathname.startsWith(item.href + "/");
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-gray-100 text-gray-900"
                        : "text-gray-500 hover:text-gray-800 hover:bg-gray-50"
                    }`}
                  >
                    <span className="text-xs">{item.icon}</span>
                    <span>{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          )}

          {/* 인증 영역 */}
          {isLoading ? (
            // 초기 복원 중: 빈 placeholder (레이아웃 흔들림 방지)
            <div className="h-7 w-20 rounded bg-gray-100 animate-pulse" />
          ) : isAuthenticated && user ? (
            // 로그인 상태
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 hidden sm:block max-w-[120px] truncate">
                {user.nickname}
              </span>
              <button
                onClick={handleLogout}
                className="px-3 py-1.5 rounded-md text-xs font-medium text-gray-500 hover:text-gray-800 hover:bg-gray-100 transition-colors"
              >
                로그아웃
              </button>
            </div>
          ) : (
            // 비로그인 상태
            <>
              {/* mock 모드 안내 */}
              {API_CONFIG.USE_MOCK && (
                <span className="text-xs text-amber-500 mr-2 hidden sm:block">
                  Mock 모드
                </span>
              )}
              <Link
                href="/login"
                className="px-3 py-1.5 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-colors"
              >
                로그인
              </Link>
              <Link
                href="/signup"
                className="px-3 py-1.5 rounded-md text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 transition-colors"
              >
                회원가입
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
