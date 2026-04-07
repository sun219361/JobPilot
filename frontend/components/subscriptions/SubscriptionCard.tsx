"use client";

import Link from "next/link";
import type { Subscription } from "@/lib/types";
import { CompanyTypeBadge } from "@/components/common/Badge";

interface SubscriptionCardProps {
  subscription: Subscription;
  onDelete: (id: number) => void;
  isDeleting?: boolean;
}

export function SubscriptionCard({
  subscription,
  onDelete,
  isDeleting = false,
}: SubscriptionCardProps) {
  const { company } = subscription;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 hover:border-gray-300 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* 기업명 + 배지 */}
          <div className="flex items-center gap-2 flex-wrap">
            <Link
              href={`/companies/${company.id}`}
              className="text-base font-semibold text-gray-900 hover:text-blue-600 transition-colors truncate"
            >
              {company.name}
            </Link>
            <CompanyTypeBadge type={company.company_type} />
          </div>
          {/* 업종 */}
          <p className="mt-0.5 text-xs text-gray-400">{company.industry}</p>
          {/* 한 줄 요약 */}
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">{company.summary}</p>
        </div>

        {/* 삭제 버튼 */}
        <button
          onClick={() => onDelete(subscription.id)}
          disabled={isDeleting}
          aria-label={`${company.name} 관심기업 삭제`}
          className="flex-shrink-0 p-1.5 rounded-md text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {isDeleting ? (
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
          ) : (
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          )}
        </button>
      </div>

      {/* 하단 링크 */}
      <div className="mt-3 pt-3 border-t border-gray-100 flex items-center gap-3">
        <Link
          href={`/companies/${company.id}`}
          className="text-xs text-blue-600 hover:text-blue-800 font-medium transition-colors"
        >
          준비 카드 보기 →
        </Link>
        {company.careers_url && (
          <a
            href={company.careers_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            채용 공고 ↗
          </a>
        )}
      </div>
    </div>
  );
}
