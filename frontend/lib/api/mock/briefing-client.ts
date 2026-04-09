import type { TodayBriefingResponse } from "@/lib/types";
import { MOCK_TODAY_BRIEFING } from "@/lib/mock/briefings";

// ─────────────────────────────────────────────
// Mock Briefing Client Interface
// ─────────────────────────────────────────────

export interface BriefingClientInterface {
  getToday(): Promise<TodayBriefingResponse>;
}

// ─────────────────────────────────────────────
// Mock Implementation
// ─────────────────────────────────────────────

export const mockBriefingClient: BriefingClientInterface = {
  async getToday() {
    await delay(400);
    return MOCK_TODAY_BRIEFING;
  },
};

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
