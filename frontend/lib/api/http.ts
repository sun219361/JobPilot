import { API_CONFIG } from "./config";
import type { ApiResponse } from "@/lib/types";

// ─────────────────────────────────────────────
// Custom Error Classes
// ─────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode?: number,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export class NetworkError extends Error {
  constructor(message = "네트워크 오류가 발생했습니다.") {
    super(message);
    this.name = "NetworkError";
  }
}

// ─────────────────────────────────────────────
// HTTP Client
// ─────────────────────────────────────────────

interface FetchOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

/**
 * 공통 fetch wrapper
 * - API_CONFIG.BASE_URL 자동 추가
 * - 성공/실패 응답 파싱
 * - 에러 unwrap
 */
export async function httpClient<T>(
  endpoint: string,
  options: FetchOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;

  // URL 구성
  let url = `${API_CONFIG.BASE_URL}${endpoint}`;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.set(key, String(value));
      }
    });
    const query = searchParams.toString();
    if (query) url += `?${query}`;
  }

  // 기본 헤더
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...fetchOptions.headers,
  };

  // Fetch 실행
  let response: Response;
  try {
    response = await fetch(url, {
      ...fetchOptions,
      headers,
    });
  } catch (err) {
    throw new NetworkError((err as Error).message);
  }

  // JSON 파싱
  let json: ApiResponse<T>;
  try {
    json = await response.json();
  } catch {
    throw new ApiError(
      "PARSE_ERROR",
      "서버 응답을 파싱할 수 없습니다.",
      response.status
    );
  }

  // 성공 여부 확인
  if (!json.success || json.error) {
    const error = json.error || { code: "UNKNOWN_ERROR", message: "알 수 없는 오류" };
    throw new ApiError(
      error.code,
      error.message,
      response.status,
      error as Record<string, unknown>
    );
  }

  return json.data;
}

// ─────────────────────────────────────────────
// HTTP Methods
// ─────────────────────────────────────────────

export const http = {
  get: <T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>) =>
    httpClient<T>(endpoint, { method: "GET", params }),

  post: <T>(endpoint: string, body?: unknown) =>
    httpClient<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown) =>
    httpClient<T>(endpoint, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    httpClient<T>(endpoint, { method: "DELETE" }),
};
