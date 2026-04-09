import { API_CONFIG } from "./config";
import { http, ApiError } from "./http";
import type { Company, CompanyDetail, PaginatedData } from "@/lib/types";
import {
  mockCompanyClient,
  type CompanyClientInterface,
} from "./mock/company-client";

// ─────────────────────────────────────────────
// Real API Client
// ─────────────────────────────────────────────

const realCompanyClient: CompanyClientInterface = {
  async getList({ q, company_type, limit = 20, offset = 0 }) {
    const params: Record<string, string | number> = { limit, offset };
    if (q) params.q = q;
    if (company_type) params.company_type = company_type;

    return http.get<PaginatedData<Company>>("/api/v1/companies", params);
  },

  async getById(id) {
    try {
      return await http.get<CompanyDetail>(`/api/v1/companies/${id}`);
    } catch (err) {
      // 404 not found 시 null 반환
      if (err instanceof ApiError && err.code === "COMPANY_NOT_FOUND") {
        return null;
      }
      throw err;
    }
  },
};

// ─────────────────────────────────────────────
// Export: mock/real 자동 선택
// ─────────────────────────────────────────────

export const companyClient: CompanyClientInterface = API_CONFIG.USE_MOCK
  ? mockCompanyClient
  : realCompanyClient;

export type { CompanyClientInterface };
