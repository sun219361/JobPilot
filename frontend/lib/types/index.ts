// ─────────────────────────────────────────────
// Auth Types (Phase 5 JWT)
// ─────────────────────────────────────────────

/** 로그인된 사용자 정보 (/api/v1/users/me 응답) */
export interface AuthUser {
  id: number;
  email: string;
  nickname: string;
  is_active: boolean;
}

/** 인증 상태 */
export type AuthState = "loading" | "authenticated" | "unauthenticated";

/** 로그인 요청 */
export interface LoginRequest {
  email: string;
  password: string;
}

/** 로그인 응답 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

/** 회원가입 요청 */
export interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
}

/** 회원가입 응답 */
export interface SignupResponse {
  id: number;
  email: string;
  nickname: string;
}

// ─────────────────────────────────────────────
// Domain Types (기존)
// ─────────────────────────────────────────────

export type CompanyType = "LARGE" | "MID" | "PUBLIC";
export type SourceType = "news" | "job" | "notice";

export interface Company {
  id: number;
  name: string;
  company_type: CompanyType;
  industry: string;
  summary: string;
  homepage_url?: string | null;
  careers_url?: string | null;
  is_active: boolean;
}

export interface PrepSnapshot {
  id: number;
  one_line_summary: string;
  recent_issue_summary: string;
  hiring_summary: string;
  talent_summary: string;
  cover_letter_points: string[];
  interview_points: string[];
  generated_at: string; // ISO 8601
}

export interface CompanyDetail extends Company {
  latest_prep_snapshot: PrepSnapshot | null;
}

export interface Subscription {
  id: number;
  company: Company;
  memo: string | null;
  created_at: string;
}

export interface SubscriptionCreateInput {
  company_id: number;
  memo?: string;
}

export interface Briefing {
  id: number;
  briefing_date: string; // YYYY-MM-DD
  title: string;
  created_at: string;
}

export interface BriefingItem {
  id: number;
  company_id: number | null;
  company_name: string | null;
  source_type: SourceType;
  headline: string;
  summary: string;
  action_point: string | null;
  sort_order: number;
}

export interface TodayBriefingResponse {
  briefing: Briefing | null;
  items: BriefingItem[];
}

// ─────────────────────────────────────────────
// API Response Types (백엔드 형식)
// ─────────────────────────────────────────────

export interface ApiError {
  code: string;
  message: string;
  limit?: number;
  current?: number;
  [key: string]: unknown;
}

export interface ApiSuccessResponse<T> {
  success: true;
  data: T;
  error: null;
}

export interface ApiErrorResponse {
  success: false;
  data: null;
  error: ApiError;
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

// ─────────────────────────────────────────────
// Pagination
// ─────────────────────────────────────────────

export interface PaginationMeta {
  limit: number;
  offset: number;
  total: number;
}

export interface PaginatedData<T> {
  items: T[];
  pagination: PaginationMeta;
}
