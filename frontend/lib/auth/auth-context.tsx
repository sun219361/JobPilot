"use client";

/**
 * auth-context.tsx
 *
 * 앱 전역 인증 상태 관리 Context.
 *
 * 상태 흐름:
 *  1. 앱 마운트 → localStorage에서 token 읽기 → /users/me 호출 → 사용자 복원
 *  2. 로그인 성공 → token 저장 + user 상태 설정
 *  3. 로그아웃 → token 제거 + user 상태 초기화
 *
 * AuthState:
 *  - "loading"         : 초기 복원 중 (앱 시작 시)
 *  - "authenticated"   : 로그인된 상태
 *  - "unauthenticated" : 로그인되지 않은 상태
 */

import React, {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
} from "react";
import type { AuthUser, AuthState } from "@/lib/types";
import { fetchMe, login as apiLogin, signup as apiSignup } from "./auth-client";
import {
  setAccessToken,
  removeAccessToken,
} from "./token-storage";
import type { LoginRequest, SignupRequest } from "@/lib/types";

// ─────────────────────────────────────────────
// Context 타입
// ─────────────────────────────────────────────

interface AuthContextValue {
  /** 현재 인증 상태 */
  authState: AuthState;
  /** 로그인된 사용자 (unauthenticated이면 null) */
  user: AuthUser | null;
  /** 로그인 */
  login: (req: LoginRequest) => Promise<void>;
  /** 회원가입 후 자동 로그인 */
  signup: (req: SignupRequest) => Promise<void>;
  /** 로그아웃 */
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// ─────────────────────────────────────────────
// AuthProvider
// ─────────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [authState, setAuthState] = useState<AuthState>("loading");
  const [user, setUser] = useState<AuthUser | null>(null);

  // 앱 시작 시 사용자 복원
  useEffect(() => {
    (async () => {
      const me = await fetchMe();
      if (me) {
        setUser(me);
        setAuthState("authenticated");
      } else {
        removeAccessToken(); // 만료된 토큰 정리
        setAuthState("unauthenticated");
      }
    })();
  }, []);

  /** 로그인: token 저장 → /me 호출 → 상태 갱신 */
  const login = useCallback(async (req: LoginRequest) => {
    const { access_token } = await apiLogin(req);
    setAccessToken(access_token);
    const me = await fetchMe();
    if (!me) throw new Error("사용자 정보를 불러올 수 없습니다.");
    setUser(me);
    setAuthState("authenticated");
  }, []);

  /**
   * 회원가입 후 자동 로그인.
   * [설계 결정] 자동 로그인을 선택한 이유:
   *  - 가입 직후 바로 서비스를 사용하게 하는 것이 UX에 더 자연스러움
   *  - 이메일 인증이 없는 MVP에서 추가 단계가 없으므로 자동 로그인이 적합
   */
  const signup = useCallback(async (req: SignupRequest) => {
    await apiSignup(req);
    // 가입 성공 → 동일 자격증명으로 자동 로그인
    await login({ email: req.email, password: req.password });
  }, [login]);

  /** 로그아웃: token 제거 + 상태 초기화 */
  const logout = useCallback(() => {
    removeAccessToken();
    setUser(null);
    setAuthState("unauthenticated");
  }, []);

  return (
    <AuthContext.Provider value={{ authState, user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ─────────────────────────────────────────────
// useAuthContext (내부용 raw hook)
// ─────────────────────────────────────────────

export function useAuthContext(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used inside <AuthProvider>");
  }
  return ctx;
}
