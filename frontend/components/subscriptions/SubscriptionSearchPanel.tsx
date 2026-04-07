"use client";

import { useState, useEffect, useRef } from "react";
import type { Company, CompanyType } from "@/lib/types";
import { CompanyTypeBadge } from "@/components/common/Badge";
import { companyClient } from "@/lib/api/company-client";

const COMPANY_TYPE_OPTIONS: { value: "" | CompanyType; label: string }[] = [
  { value: "", label: "전체" },
  { value: "LARGE", label: "대기업" },
  { value: "MID", label: "중견기업" },
  { value: "PUBLIC", label: "공기업" },
];

interface SubscriptionSearchPanelProps {
  subscribedCompanyIds: number[];
  onAdd: (companyId: number) => Promise<void>;
  onClose: () => void;
}

export function SubscriptionSearchPanel({
  subscribedCompanyIds,
  onAdd,
  onClose,
}: SubscriptionSearchPanelProps) {
  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<"" | CompanyType>("");
  const [results, setResults] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [addingId, setAddingId] = useState<number | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 패널 열릴 때 input 포커스
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // 검색 실행 (debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchResults();
    }, 250);
    return () => clearTimeout(timer);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, typeFilter]);

  async function fetchResults() {
    setIsLoading(true);
    try {
      const res = await companyClient.getList({
        q: query || undefined,
        company_type: typeFilter || undefined,
        limit: 30,
      });
      setResults(res.items);
    } catch {
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }

  async function handleAdd(companyId: number) {
    setAddingId(companyId);
    try {
      await onAdd(companyId);
    } finally {
      setAddingId(null);
    }
  }

  // 배경 클릭으로 닫기
  function handleBackdropClick(e: React.MouseEvent<HTMLDivElement>) {
    if (e.target === e.currentTarget) onClose();
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40 px-0 sm:px-4"
      onClick={handleBackdropClick}
    >
      <div className="w-full sm:max-w-lg bg-white rounded-t-2xl sm:rounded-xl shadow-xl flex flex-col max-h-[85vh]">
        {/* 헤더 */}
        <div className="flex items-center justify-between px-4 pt-4 pb-3 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-900">관심기업 추가</h2>
          <button
            onClick={onClose}
            className="p-1.5 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
            aria-label="닫기"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* 검색 + 필터 */}
        <div className="px-4 py-3 space-y-2 border-b border-gray-100">
          {/* 검색 인풋 */}
          <div className="relative">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 111 11a6 6 0 0116 0z" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="기업명 또는 업종으로 검색"
              className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
            />
          </div>

          {/* 유형 필터 */}
          <div className="flex gap-1.5">
            {COMPANY_TYPE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setTypeFilter(opt.value)}
                className={`px-2.5 py-1 text-xs font-medium rounded-full border transition-colors ${
                  typeFilter === opt.value
                    ? "bg-gray-900 text-white border-gray-900"
                    : "bg-white text-gray-600 border-gray-200 hover:border-gray-400"
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* 검색 결과 */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center py-10">
              <svg className="w-5 h-5 animate-spin text-gray-400" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
            </div>
          ) : results.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-sm text-gray-400">
              <span className="text-2xl mb-2">🔍</span>
              <span>검색 결과가 없습니다</span>
            </div>
          ) : (
            <ul className="divide-y divide-gray-100">
              {results.map((company) => {
                const isSubscribed = subscribedCompanyIds.includes(company.id);
                const isAdding = addingId === company.id;

                return (
                  <li key={company.id} className="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition-colors">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="text-sm font-medium text-gray-900 truncate">{company.name}</span>
                        <CompanyTypeBadge type={company.company_type} size="sm" />
                      </div>
                      <p className="text-xs text-gray-400 mt-0.5">{company.industry}</p>
                    </div>
                    <button
                      onClick={() => !isSubscribed && handleAdd(company.id)}
                      disabled={isSubscribed || isAdding}
                      className={`flex-shrink-0 px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                        isSubscribed
                          ? "bg-gray-100 text-gray-400 cursor-default"
                          : isAdding
                          ? "bg-blue-50 text-blue-400 cursor-not-allowed"
                          : "bg-blue-600 text-white hover:bg-blue-700"
                      }`}
                    >
                      {isSubscribed ? "등록됨" : isAdding ? "추가 중…" : "추가"}
                    </button>
                  </li>
                );
              })}
            </ul>
          )}
        </div>

        {/* 하단 안내 */}
        <div className="px-4 py-3 border-t border-gray-100 bg-gray-50 rounded-b-xl">
          <p className="text-xs text-gray-400 text-center">
            최대 5개 기업을 관심기업으로 등록할 수 있습니다
          </p>
        </div>
      </div>
    </div>
  );
}
