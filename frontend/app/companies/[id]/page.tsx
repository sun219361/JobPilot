"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, notFound } from "next/navigation";
import Link from "next/link";
import type { CompanyDetail, Subscription } from "@/lib/types";
import { companyClient } from "@/lib/api/company-client";
import { subscriptionClient, SubscriptionLimitError, DuplicateSubscriptionError } from "@/lib/api/subscription-client";
import { CompanyHero } from "@/components/companies/CompanyHero";
import { PrepSnapshotCard } from "@/components/companies/PrepSnapshotCard";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CompanyDetailSkeleton } from "@/components/common/LoadingSkeleton";

type PageState = "loading" | "success" | "notfound" | "error";

export default function CompanyDetailPage() {
  const params = useParams();
  const companyId = Number(params.id);

  const [state, setState] = useState<PageState>("loading");
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [isToggling, setIsToggling] = useState(false);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const loadCompany = useCallback(async () => {
    if (!companyId || isNaN(companyId)) {
      setState("notfound");
      return;
    }
    setState("loading");
    try {
      const [detail, subs] = await Promise.all([
        companyClient.getById(companyId),
        subscriptionClient.getList(),
      ]);
      if (!detail) {
        setState("notfound");
        return;
      }
      setCompany(detail);
      setSubscriptions(subs);
      setState("success");
    } catch {
      setState("error");
    }
  }, [companyId]);

  useEffect(() => {
    loadCompany();
  }, [loadCompany]);

  function showToast(msg: string) {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  }

  const isSubscribed = subscriptions.some((s) => s.company.id === companyId);

  async function handleToggleSubscription() {
    if (!company) return;
    setIsToggling(true);
    try {
      if (isSubscribed) {
        const sub = subscriptions.find((s) => s.company.id === companyId);
        if (sub) {
          await subscriptionClient.delete(sub.id);
          setSubscriptions((prev) => prev.filter((s) => s.id !== sub.id));
          showToast("관심기업에서 해제했습니다.");
        }
      } else {
        const newSub = await subscriptionClient.create({ company_id: companyId });
        setSubscriptions((prev) => [...prev, newSub]);
        showToast(`${company.name}을(를) 관심기업에 추가했습니다.`);
      }
    } catch (err) {
      if (err instanceof SubscriptionLimitError) {
        showToast(`관심기업은 최대 ${err.limit}개까지 등록 가능합니다.`);
      } else if (err instanceof DuplicateSubscriptionError) {
        showToast("이미 등록된 기업입니다.");
      } else {
        showToast("오류가 발생했습니다.");
      }
    } finally {
      setIsToggling(false);
    }
  }

  // 상태별 렌더링
  if (state === "loading") {
    return (
      <div className="space-y-4">
        <div className="h-5 w-24 bg-gray-200 rounded animate-pulse" />
        <CompanyDetailSkeleton />
      </div>
    );
  }

  if (state === "notfound") {
    return (
      <div className="space-y-4">
        <Link href="/subscriptions" className="text-sm text-gray-400 hover:text-gray-600">
          ← 관심기업 목록
        </Link>
        <EmptyState
          icon="🔍"
          title="기업을 찾을 수 없습니다"
          description="존재하지 않거나 삭제된 기업입니다."
          action={
            <Link
              href="/subscriptions"
              className="px-4 py-2 rounded-lg bg-gray-900 text-white text-sm font-medium hover:bg-gray-700 transition-colors"
            >
              관심기업 목록으로
            </Link>
          }
        />
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="space-y-4">
        <Link href="/subscriptions" className="text-sm text-gray-400 hover:text-gray-600">
          ← 관심기업 목록
        </Link>
        <ErrorState onRetry={loadCompany} />
      </div>
    );
  }

  if (!company) return null;

  return (
    <div className="space-y-4">
      {/* 뒤로가기 */}
      <Link href="/subscriptions" className="inline-flex items-center text-sm text-gray-400 hover:text-gray-600 transition-colors">
        <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
        관심기업 목록
      </Link>

      {/* 기업 헤더 */}
      <CompanyHero
        company={company}
        isSubscribed={isSubscribed}
        onToggleSubscription={handleToggleSubscription}
        isToggling={isToggling}
      />

      {/* 준비 카드 */}
      {company.latest_prep_snapshot ? (
        <PrepSnapshotCard snapshot={company.latest_prep_snapshot} />
      ) : (
        <EmptyState
          icon="📝"
          title="준비 카드가 아직 없습니다"
          description="배치 실행 후 준비 카드가 생성됩니다."
        />
      )}

      {/* 토스트 */}
      {toastMsg && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm shadow-lg whitespace-nowrap">
          {toastMsg}
        </div>
      )}
    </div>
  );
}
