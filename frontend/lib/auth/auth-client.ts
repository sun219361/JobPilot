/**
 * auth-client.ts
 *
 * 인증 관련 API 호출 클라이언트.
 * - signup: POST /api/v1/auth/signup
 * - login:  POST /api/v1/auth/login  → access_token 반환
 * - me:     GET  /api/v1/users/me    → 현재 사용자 정보 반환
 *
 * mock 모드에서는 로그인 기능이 비활성화됩니다.
 * (mock 모드는 백엔드 없이 UI 개발용이므로 인증 흐름을 지원하지 않습니다.)
 */

import { API_CONFIG } from "@/lib/api/config";
import { getAccessToken } from "./token-storage";
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  SignupRequest,
  SignupResponse,
} from "@/lib/types";

const BASE = API_CONFIG.BASE_URL;

/** fetch + JSON 파싱 + 에러 언래핑 공통 헬퍼 */
async function authFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const res = await fetch(`${BASE}${endpoint}`, { ...options, headers });
  const json = await res.json();

  if (!json.success || json.error) {
    const msg = json.error?.message ?? "요청에 실패했습니다.";
    throw new Error(msg);
  }
  return json.data as T;
}

/** 회원가입 */
export async function signup(req: SignupRequest): Promise<SignupResponse> {
  return authFetch<SignupResponse>("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/** 로그인 → access_token 반환 */
export async function login(req: LoginRequest): Promise<LoginResponse> {
  return authFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

/**
 * 현재 사용자 조회 (토큰 검증용)
 * 토큰이 없거나 만료됐으면 null 반환 (예외를 외부로 throw하지 않음)
 */
export async function fetchMe(): Promise<AuthUser | null> {
  const token = getAccessToken();
  if (!token) return null;

  try {
    return await authFetch<AuthUser>("/api/v1/users/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
  } catch {
    return null;
  }
}
