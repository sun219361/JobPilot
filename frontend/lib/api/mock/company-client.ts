import type { Company, CompanyDetail, PaginatedData } from "@/lib/types";
import { MOCK_COMPANIES, getMockCompanyDetail } from "@/lib/mock/companies";

// ─────────────────────────────────────────────
// Mock Company Client Interface
// ─────────────────────────────────────────────

export interface CompanyClientInterface {
  getList(params: {
    q?: string;
    company_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<PaginatedData<Company>>;
  
  getById(id: number): Promise<CompanyDetail | null>;
}

// ─────────────────────────────────────────────
// Mock Implementation
// ─────────────────────────────────────────────

export const mockCompanyClient: CompanyClientInterface = {
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

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
