import type { Subscription, SubscriptionCreateInput } from "@/lib/types";
import { MOCK_SUBSCRIPTIONS } from "@/lib/mock/subscriptions";
import { MOCK_COMPANIES } from "@/lib/mock/companies";

// ─────────────────────────────────────────────
// Error Classes
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
// Mock Subscription Client Interface
// ─────────────────────────────────────────────

export interface SubscriptionClientInterface {
  getList(): Promise<Subscription[]>;
  create(input: SubscriptionCreateInput): Promise<Subscription>;
  delete(subscriptionId: number): Promise<void>;
}

// ─────────────────────────────────────────────
// In-memory Store (mock 전용)
// ─────────────────────────────────────────────

let _store: Subscription[] = [...MOCK_SUBSCRIPTIONS];
let _nextId = 100;

const SUBSCRIPTION_LIMIT = 5;

// ─────────────────────────────────────────────
// Mock Implementation
// ─────────────────────────────────────────────

export const mockSubscriptionClient: SubscriptionClientInterface = {
  async getList() {
    await delay(300);
    return [..._store].sort(
      (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    );
  },

  async create({ company_id, memo }) {
    await delay(300);

    const company = MOCK_COMPANIES.find((c) => c.id === company_id && c.is_active);
    if (!company) throw new CompanyNotFoundError();

    if (_store.some((s) => s.company.id === company_id)) {
      throw new DuplicateSubscriptionError();
    }

    if (_store.length >= SUBSCRIPTION_LIMIT) {
      throw new SubscriptionLimitError(SUBSCRIPTION_LIMIT, _store.length);
    }

    const newSub: Subscription = {
      id: _nextId++,
      company,
      memo: memo ?? null,
      created_at: new Date().toISOString(),
    };
    _store = [newSub, ..._store];
    return newSub;
  },

  async delete(subscriptionId) {
    await delay(200);
    _store = _store.filter((s) => s.id !== subscriptionId);
  },
};

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
