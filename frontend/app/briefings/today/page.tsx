"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import type { TodayBriefingResponse, BriefingItem } from "@/lib/types";
import { briefingClient } from "@/lib/api/briefing-client";
import { BriefingHeader } from "@/components/briefings/BriefingHeader";
import { BriefingItemCard } from "@/components/briefings/BriefingItemCard";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { ListSkeleton, BriefingItemSkeleton } from "@/components/common/LoadingSkeleton";

type PageState = "loading" | "success" | "empty" | "error";

// 기업별로 브리핑 아이템 그룹핑
function groupByCompany(items: BriefingItem[]): Map<string, BriefingItem[]> {
  const map = new Map<string, BriefingItem[]>();
  for (const item of items) {
    const key = item.company_name ?? "기타";
    const group = map.get(key) ?? [];
    group.push(item);
    map.set(key, group);
  }
  return map;
}

export default function TodayBriefingPage() {
  const [state, setState] = useState<PageState>("loading");
  const [data, setData] = useState<TodayBriefingResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true);
    } else {
      setState("loading");
    }
    try {
      const res = await briefingClient.getToday();
      setData(res);
      setState(res.briefing && res.items.length > 0 ? "success" : "empty");
    } catch {
      setState("error");
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(false);
  }, [load]);

  function handleRefresh() {
    load(true);
  }

  // ── 로딩 ────────────────────────────────────
  if (state === "loading") {
    return (
      <div className="space-y-4">
        <div className="rounded-lg border border-gray-200 bg-white px-5 py-4 space-y-2">
          <div className="h-3 w-20 bg-gray-200 rounded animate-pulse" />
          <div className="h-5 w-48 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 w-36 bg-gray-200 rounded animate-pulse" />
        </div>
        <ListSkeleton count={4} Item={BriefingItemSkeleton} />
      </div>
    );
  }

  // ── 에러 ────────────────────────────────────
  if (state === "error") {
    return <ErrorState onRetry={() => load(false)} />;
  }

  // ── 빈 상태 ─────────────────────────────────
  if (state === "empty" || !data?.briefing) {
    return (
      <EmptyState
        icon="📭"
        title="오늘 브리핑이 아직 없습니다"
        description={
          "관심기업을 등록하면 내일 아침부터\n브리핑이 생성됩니다."
        }
        action={
          <Link
            href="/subscriptions"
            className="px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            관심기업 등록하러 가기
          </Link>
        }
      />
    );
  }

  // ── 성공 ────────────────────────────────────
  const sortedItems = [...data.items].sort((a, b) => a.sort_order - b.sort_order);
  const grouped = groupByCompany(sortedItems);

  return (
    <div className="space-y-4">
      {/* 헤더 */}
      <BriefingHeader
        briefing={data.briefing}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      {/* 기업별 그룹 */}
      {Array.from(grouped.entries()).map(([companyName, items]) => (
        <section key={companyName}>
          {/* 기업명 구분자 */}
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide px-1 mb-2">
            {companyName}
          </h3>
          <div className="space-y-2.5">
            {items.map((item) => (
              <BriefingItemCard key={item.id} item={item} />
            ))}
          </div>
        </section>
      ))}

      {/* 안내 */}
      <p className="text-xs text-gray-400 text-center pb-2">
        매일 오전 6시에 업데이트됩니다 · Phase 0은 mock 데이터
      </p>
    </div>
  );
}
