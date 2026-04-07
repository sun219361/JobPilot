import type { Company, CompanyDetail, PaginatedResponse } from "@/lib/types";
import { MOCK_COMPANIES, getMockCompanyDetail } from "@/lib/mock/companies";

// ─────────────────────────────────────────────
// Interface (실제 API 교체 시 이 인터페이스만 구현하면 됨)
// ─────────────────────────────────────────────

export interface CompanyClientInterface {
  getList(params: {
    q?: string;
    company_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedResponse<Company>>;
  getById(id: number): Promise<CompanyDetail | null>;
}

// ─────────────────────────────────────────────
// Mock Client (초기 구현)
// ─────────────────────────────────────────────

const mockCompanyClient: CompanyClientInterface = {
  async getList({ q, company_type, limit = 20, offset = 0 }) {
    await delay(300);
    let items = MOCK_COMPANIES.filter((c) => c.is_active);

    if (q) {
      const lower = q.toLowerCase();
      items = items.filter(
        (c) =>
          c.name.toLowerCase().includes(lower) ||
          c.industry.toLowerCase().includes(lower)
      );
    }
    if (company_type) {
      items = items.filter((c) => c.company_type === company_type);
    }

    const total = items.length;
    const paged = items.slice(offset, offset + limit);
    return { items: paged, pagination: { limit, offset, total } };
  },

  async getById(id) {
    await delay(300);
    return getMockCompanyDetail(id);
  },
};

// ─────────────────────────────────────────────
// Real API Client (백엔드 연결 시 이 클라이언트로 교체)
// ─────────────────────────────────────────────

// const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
//
// const realCompanyClient: CompanyClientInterface = {
//   async getList({ q, company_type, limit = 20, offset = 0 }) {
//     const params = new URLSearchParams();
//     if (q) params.set("q", q);
//     if (company_type) params.set("company_type", company_type);
//     params.set("limit", String(limit));
//     params.set("offset", String(offset));
//     const res = await fetch(`${API_BASE}/api/v1/companies?${params}`);
//     const json = await res.json();
//     return json.data;
//   },
//   async getById(id) {
//     const res = await fetch(`${API_BASE}/api/v1/companies/${id}`);
//     const json = await res.json();
//     return json.success ? json.data : null;
//   },
// };

// ─────────────────────────────────────────────
// Export: mock ↔ real 교체 시 아래 한 줄만 변경
// ─────────────────────────────────────────────

export const companyClient: CompanyClientInterface = mockCompanyClient;

// ─────────────────────────────────────────────
// Helper
// ─────────────────────────────────────────────

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
