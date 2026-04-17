/**
 * token-storage.ts
 *
 * JWT access token localStorage 유틸리티.
 *
 * [MVP 설계 결정] localStorage 사용 이유:
 *  - 구현 단순성: 서버 없이 클라이언트 단독으로 토큰 관리 가능
 *  - 새로고침 후에도 로그인 상태 유지 가능
 *  - MVP에서 빠른 구현과 디버깅에 유리
 *
 * [향후 개선 방향]:
 *  - httpOnly Cookie 방식으로 전환하면 XSS 공격으로부터 토큰 보호 가능
 *  - Next.js middleware + server-side cookie 검증으로 SSR 보호 페이지 구현 가능
 *  - 현재 localStorage 방식은 XSS 취약점이 존재하므로, 운영 환경에서는
 *    반드시 Content-Security-Policy 헤더와 함께 사용할 것
 */

const TOKEN_KEY = "jobpilot_access_token";

/** 저장된 access token 반환. 없으면 null. */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/** access token을 localStorage에 저장 */
export function setAccessToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

/** access token 제거 (로그아웃) */
export function removeAccessToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}
