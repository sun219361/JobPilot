"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import type { CompanyDetail } from "@/lib/types";
import { companyClient } from "@/lib/api/company-client";
import { subscriptionClient } from "@/lib/api/subscription-client";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CompanyDetailSkeleton } from "@/components/common/LoadingSkeleton";
import { CompanyHero } from "@/components/companies/CompanyHero";
import { PrepSnapshotCard } from "@/components/companies/PrepSnapshotCard";

type PageState = "loading" | "success" | "not-found" | "error";

export default function CompanyDetailPage() {
  const params = useParams();
  const companyId = Number(params.id);

  const [state, setState] = useState<PageState>("loading");
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  useEffect(() => {
    load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyId]);

  async function load() {
    setState("loading");
    try {
      const [companyData, subsData] = await Promise.all([
        companyClient.getById(companyId),
        subscriptionClient.getList(),
      ]);

      if (!companyData) {
        setState("not-found");
        return;
      }

      setCompany(companyData);
      setIsSubscribed(subsData.some((s) => s.company.id === companyId));
      setState("success");
    } catch {
      setState("error");
    }
  }

  async function handleToggleSubscription() {
    if (!company) return;
    setIsToggling(true);

    try {
      if (isSubscribed) {
        const subs = await subscriptionClient.getList();
        const sub = subs.find((s) => s.company.id === companyId);
        if (sub) {
          await subscriptionClient.delete(sub.id);
          setIsSubscribed(false);
        }
      } else {
        await subscriptionClient.create({ company_id: companyId });
        setIsSubscribed(true);
      }
    } catch {
      // 에러는 무시 (toast가 있으면 표시 가능)
    } finally {
      setIsToggling(false);
    }
  }

  return (
    <div className="space-y-4">
      {state === "loading" && (
        <>
          <PageHeader title="기업 정보 로딩 중..." />
          <CompanyDetailSkeleton />
        </>
      )}

      {state === "error" && (
        <>
          <PageHeader title="오류" />
          <ErrorState onRetry={load} />
        </>
      )}

      {state === "not-found" && (
        <>
          <PageHeader title="기업을 찾을 수 없습니다" />
          <EmptyState
            icon="🔍"
            title="존재하지 않는 기업입니다"
            description="기업 정보를 불러올 수 없습니다."
          />
        </>
      )}

      {state === "success" && company && (
        <>
          <CompanyHero
            company={company}
            isSubscribed={isSubscribed}
            onToggleSubscription={handleToggleSubscription}
            isToggling={isToggling}
          />

          {company.latest_prep_snapshot ? (
            <PrepSnapshotCard snapshot={company.latest_prep_snapshot} />
          ) : (
            <EmptyState
              icon="📋"
              title="준비 카드가 아직 없습니다"
              description="곧 이 기업의 채용 준비 정보를 제공할 예정입니다."
            />
          )}
        </>
      )}
    </div>
  );
}
