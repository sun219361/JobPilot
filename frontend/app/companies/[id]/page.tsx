"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import type { CompanyDetail } from "@/lib/types";
import { companyClient } from "@/lib/api/company-client";
import { subscriptionClient } from "@/lib/api/subscription-client";
import { useAuth } from "@/lib/auth/use-auth";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { CompanyDetailSkeleton } from "@/components/common/LoadingSkeleton";
import { CompanyHero } from "@/components/companies/CompanyHero";
import { PrepSnapshotCard } from "@/components/companies/PrepSnapshotCard";

type PageState = "loading" | "success" | "not-found" | "error";

export default function CompanyDetailPage() {
  const params = useParams();
  const router = useRouter();
  const companyId = Number(params.id);
  const { isAuthenticated } = useAuth();

  const [state, setState] = useState<PageState>("loading");
  const [company, setCompany] = useState<CompanyDetail | null>(null);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  useEffect(() => {
    load();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [companyId, isAuthenticated]);

  async function load() {
    setState("loading");
    try {
      // 기업 상세는 공개 API — 인증 불필요
      const companyData = await companyClient.getById(companyId);

      if (!companyData) {
        setState("not-found");
        return;
      }

      setCompany(companyData);

      // 구독 여부는 인증된 사용자에게만 조회 (비인증 시 false 유지)
      if (isAuthenticated) {
        try {
          const subsData = await subscriptionClient.getList();
          setIsSubscribed(subsData.some((s) => s.company.id === companyId));
        } catch {
          // 구독 조회 실패는 페이지 전체 에러로 처리하지 않음
          setIsSubscribed(false);
        }
      } else {
        setIsSubscribed(false);
      }

      setState("success");
    } catch {
      setState("error");
    }
  }

  async function handleToggleSubscription() {
    // 비인증 사용자가 관심기업 버튼 클릭 시 로그인 페이지로 유도
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }

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
      // 에러 무시 (향후 toast 추가 가능)
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
