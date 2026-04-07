import type { TodayBriefingResponse } from "@/lib/types";
import { MOCK_TODAY_BRIEFING } from "@/lib/mock/briefings";

// ─────────────────────────────────────────────
// Interface
// ─────────────────────────────────────────────

export interface BriefingClientInterface {
  getToday(): Promise<TodayBriefingResponse>;
}

// ─────────────────────────────────────────────
// Mock Client
// ─────────────────────────────────────────────

const mockBriefingClient: BriefingClientInterface = {
  async getToday() {
    await delay(400);
    return MOCK_TODAY_BRIEFING;
  },
};

// ─────────────────────────────────────────────
// Real API Client (백엔드 연결 시 교체)
// ─────────────────────────────────────────────

// const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
//
// const realBriefingClient: BriefingClientInterface = {
//   async getToday() {
//     const res = await fetch(`${API_BASE}/api/v1/briefings/today`);
//     const json = await res.json();
//     if (!json.success) throw new Error(json.error?.message);
//     return json.data;
//   },
// };

// ─────────────────────────────────────────────
// Export
// ─────────────────────────────────────────────

export const briefingClient: BriefingClientInterface = mockBriefingClient;

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
