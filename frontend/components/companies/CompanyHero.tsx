"use client";

import type { CompanyDetail } from "@/lib/types";
import { CompanyTypeBadge } from "@/components/common/Badge";

interface CompanyHeroProps {
  company: CompanyDetail;
  isSubscribed: boolean;
  onToggleSubscription: () => void;
  isToggling: boolean;
}

export function CompanyHero({
  company,
  isSubscribed,
  onToggleSubscription,
  isToggling,
}: CompanyHeroProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      {/* 기업명 + 배지 + 버튼 */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-bold text-gray-900 leading-tight">{company.name}</h1>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <CompanyTypeBadge type={company.company_type} />
            <span className="text-xs text-gray-400">{company.industry}</span>
          </div>
        </div>

        <button
          onClick={onToggleSubscription}
          disabled={isToggling}
          className={`flex-shrink-0 flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
            isSubscribed
              ? "bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-600 border border-gray-200"
              : "bg-blue-600 text-white hover:bg-blue-700"
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isToggling ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          ) : isSubscribed ? (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          )}
          {isSubscribed ? "관심기업 해제" : "관심기업 추가"}
        </button>
      </div>

      {/* 한 줄 요약 */}
      <p className="mt-3 text-sm text-gray-600 leading-relaxed">{company.summary}</p>

      {/* 링크 */}
      {(company.homepage_url || company.careers_url) && (
        <div className="mt-3 flex items-center gap-3">
          {company.homepage_url && (
            <a
              href={company.homepage_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
            >
              공식 홈페이지 ↗
            </a>
          )}
          {company.careers_url && (
            <a
              href={company.careers_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-blue-500 hover:text-blue-700 font-medium transition-colors"
            >
              채용 공고 ↗
            </a>
          )}
        </div>
      )}
    </div>
  );
}
