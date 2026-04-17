/**
 * use-auth.ts
 *
 * 컴포넌트에서 사용하는 공개 auth hook.
 * AuthContext의 값을 래핑하여 편리한 파생 상태를 추가로 제공한다.
 */

"use client";

import { useAuthContext } from "./auth-context";

export function useAuth() {
  const { authState, user, login, signup, logout } = useAuthContext();

  return {
    /** 현재 인증 상태: "loading" | "authenticated" | "unauthenticated" */
    authState,
    /** 로그인된 사용자 객체. 비로그인이면 null */
    user,
    /** 초기 복원 중 여부 */
    isLoading: authState === "loading",
    /** 로그인 여부 */
    isAuthenticated: authState === "authenticated",
    /** 로그인 함수 */
    login,
    /** 회원가입 + 자동 로그인 함수 */
    signup,
    /** 로그아웃 함수 */
    logout,
  };
}
