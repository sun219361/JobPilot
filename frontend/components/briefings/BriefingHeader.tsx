import type { Briefing } from "@/lib/types";
import { formatDate } from "@/lib/utils/format";

interface BriefingHeaderProps {
  briefing: Briefing;
  onRefresh: () => void;
  isRefreshing: boolean;
}

export function BriefingHeader({ briefing, onRefresh, isRefreshing }: BriefingHeaderProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white px-5 py-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-gray-400 uppercase tracking-wide mb-1">
            오늘의 브리핑
          </p>
          <h2 className="text-base font-semibold text-gray-900">{briefing.title}</h2>
          <p className="mt-0.5 text-sm text-gray-500">{formatDate(briefing.briefing_date)}</p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          aria-label="새로고침"
          className="flex-shrink-0 p-2 rounded-lg border border-gray-200 text-gray-500 hover:border-gray-400 hover:text-gray-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <svg
            className={`w-4 h-4 ${isRefreshing ? "animate-spin" : ""}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
