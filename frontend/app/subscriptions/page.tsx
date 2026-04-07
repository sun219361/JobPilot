"use client";

import { useState, useEffect, useCallback } from "react";
import type { Subscription } from "@/lib/types";
import { subscriptionClient, SubscriptionLimitError, DuplicateSubscriptionError } from "@/lib/api/subscription-client";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { ListSkeleton, CompanyCardSkeleton } from "@/components/common/LoadingSkeleton";
import { SubscriptionCard } from "@/components/subscriptions/SubscriptionCard";
import { SubscriptionSearchPanel } from "@/components/subscriptions/SubscriptionSearchPanel";

type PageState = "loading" | "success" | "error";

export default function SubscriptionsPage() {
  const [state, setState] = useState<PageState>("loading");
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);

  const load = useCallback(async () => {
    setState("loading");
    setErrorMsg(null);
    try {
      const subs = await subscriptionClient.getList();
      setSubscriptions(subs);
      setState("success");
    } catch {
      setState("error");
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  // 토스트 표시
  function showToast(msg: string) {
    setToastMsg(msg);
    setTimeout(() => setToastMsg(null), 3000);
  }

  // 관심기업 삭제
  async function handleDelete(subscriptionId: number) {
    setDeletingId(subscriptionId);
    try {
      await subscriptionClient.delete(subscriptionId);
      setSubscriptions((prev) => prev.filter((s) => s.id !== subscriptionId));
      showToast("관심기업이 삭제되었습니다.");
    } catch {
      showToast("삭제 중 오류가 발생했습니다.");
    } finally {
      setDeletingId(null);
    }
  }

  // 관심기업 추가 (SearchPanel에서 호출)
  async function handleAdd(companyId: number) {
    try {
      const newSub = await subscriptionClient.create({ company_id: companyId });
      setSubscriptions((prev) => [newSub, ...prev]);
      showToast(`${newSub.company.name}을(를) 관심기업에 추가했습니다.`);
    } catch (err) {
      if (err instanceof SubscriptionLimitError) {
        showToast(`관심기업은 최대 ${err.limit}개까지 등록 가능합니다.`);
      } else if (err instanceof DuplicateSubscriptionError) {
        showToast("이미 등록된 기업입니다.");
      } else {
        showToast("추가 중 오류가 발생했습니다.");
      }
      throw err; // SearchPanel에서 버튼 상태 복원을 위해 re-throw
    }
  }

  const subscribedIds = subscriptions.map((s) => s.company.id);

  return (
    <div className="space-y-4">
      <PageHeader
        title="관심기업 관리"
        description={
          state === "success"
            ? `${subscriptions.length}개 등록됨 · 최대 5개`
            : undefined
        }
        action={
          <button
            onClick={() => setIsSearchOpen(true)}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
            </svg>
            기업 추가
          </button>
        }
      />

      {/* 본문 */}
      {state === "loading" && (
        <ListSkeleton count={3} Item={CompanyCardSkeleton} />
      )}

      {state === "error" && (
        <ErrorState onRetry={load} />
      )}

      {state === "success" && subscriptions.length === 0 && (
        <EmptyState
          icon="⭐"
          title="아직 관심기업이 없습니다"
          description="기업을 추가하면 뉴스와 채용 공고를 매일 브리핑으로 받아볼 수 있습니다."
          action={
            <button
              onClick={() => setIsSearchOpen(true)}
              className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              첫 관심기업 추가하기
            </button>
          }
        />
      )}

      {state === "success" && subscriptions.length > 0 && (
        <div className="space-y-3">
          {subscriptions.map((sub) => (
            <SubscriptionCard
              key={sub.id}
              subscription={sub}
              onDelete={handleDelete}
              isDeleting={deletingId === sub.id}
            />
          ))}
        </div>
      )}

      {/* 검색 패널 */}
      {isSearchOpen && (
        <SubscriptionSearchPanel
          subscribedCompanyIds={subscribedIds}
          onAdd={handleAdd}
          onClose={() => setIsSearchOpen(false)}
        />
      )}

      {/* 토스트 메시지 */}
      {toastMsg && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-lg bg-gray-900 text-white text-sm shadow-lg whitespace-nowrap animate-fade-in">
          {toastMsg}
        </div>
      )}
    </div>
  );
}
