import { API_CONFIG } from "./config";
import { http, ApiError } from "./http";
import type { Subscription, SubscriptionCreateInput } from "@/lib/types";
import {
  mockSubscriptionClient,
  type SubscriptionClientInterface,
  SubscriptionLimitError as MockLimitError,
  DuplicateSubscriptionError as MockDuplicateError,
  CompanyNotFoundError as MockNotFoundError,
} from "./mock/subscription-client";

// ─────────────────────────────────────────────
// Error Classes (백엔드 응답 → 프론트 에러 변환)
// ─────────────────────────────────────────────

export class SubscriptionLimitError extends Error {
  constructor(public limit: number, public current: number) {
    super(`관심기업은 최대 ${limit}개까지 등록할 수 있습니다.`);
    this.name = "SubscriptionLimitError";
  }
}

export class DuplicateSubscriptionError extends Error {
  constructor() {
    super("이미 등록된 관심기업입니다.");
    this.name = "DuplicateSubscriptionError";
  }
}

export class CompanyNotFoundError extends Error {
  constructor() {
    super("해당 기업을 찾을 수 없습니다.");
    this.name = "CompanyNotFoundError";
  }
}

// ─────────────────────────────────────────────
// Real API Client
// ─────────────────────────────────────────────

const realSubscriptionClient: SubscriptionClientInterface = {
  async getList() {
    const data = await http.get<{ items: Subscription[] }>("/api/v1/subscriptions");
    return data.items;
  },

  async create(input) {
    try {
      return await http.post<Subscription>("/api/v1/subscriptions", input);
    } catch (err) {
      if (err instanceof ApiError) {
        // 백엔드 에러 코드를 프론트 에러로 변환
        if (err.code === "SUBSCRIPTION_LIMIT_EXCEEDED") {
          const { limit = 5, current = 0 } = err.details || {};
          throw new SubscriptionLimitError(Number(limit), Number(current));
        }
        if (err.code === "DUPLICATE_SUBSCRIPTION") {
          throw new DuplicateSubscriptionError();
        }
        if (err.code === "COMPANY_NOT_FOUND") {
          throw new CompanyNotFoundError();
        }
      }
      throw err;
    }
  },

  async delete(subscriptionId) {
    await http.delete(`/api/v1/subscriptions/${subscriptionId}`);
  },
};

// ─────────────────────────────────────────────
// Export: mock/real 자동 선택
// ─────────────────────────────────────────────

export const subscriptionClient: SubscriptionClientInterface = API_CONFIG.USE_MOCK
  ? mockSubscriptionClient
  : realSubscriptionClient;

// Mock 에러도 export (타입 체크용)
export {
  MockLimitError,
  MockDuplicateError,
  MockNotFoundError,
};

export type { SubscriptionClientInterface };
