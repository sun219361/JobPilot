"use client";

import { useState, useEffect } from "react";
import type { TodayBriefingResponse } from "@/lib/types";
import { briefingClient } from "@/lib/api/briefing-client";
import { PageHeader } from "@/components/common/PageHeader";
import { EmptyState } from "@/components/common/EmptyState";
import { ErrorState } from "@/components/common/ErrorState";
import { ListSkeleton, BriefingItemSkeleton } from "@/components/common/LoadingSkeleton";
import { BriefingHeader } from "@/components/briefings/BriefingHeader";
import { BriefingItemCard } from "@/components/briefings/BriefingItemCard";

type PageState = "loading" | "success" | "error";

export default function TodayBriefingPage() {
  const [state, setState] = useState<PageState>("loading");
  const [data, setData] = useState<TodayBriefingResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setState("loading");
    try {
      const result = await briefingClient.getToday();
      setData(result);
      setState("success");
    } catch {
      setState("error");
    }
  }

  async function handleRefresh() {
    setIsRefreshing(true);
    try {
      const result = await briefingClient.getToday();
      setData(result);
    } catch {
      // 에러 무시
    } finally {
      setIsRefreshing(false);
    }
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="오늘의 브리핑"
        description="관심기업의 최신 소식을 확인하세요"
      />

      {state === "loading" && (
        <ListSkeleton count={3} Item={BriefingItemSkeleton} />
      )}

      {state === "error" && (
        <ErrorState onRetry={load} />
      )}

      {state === "success" && data && (
        <>
          {data.briefing ? (
            <>
              <BriefingHeader
                briefing={data.briefing}
                onRefresh={handleRefresh}
                isRefreshing={isRefreshing}
              />
              {data.items.length > 0 ? (
                <div className="space-y-3">
                  {data.items.map((item) => (
                    <BriefingItemCard key={item.id} item={item} />
                  ))}
                </div>
              ) : (
                <EmptyState
                  icon="📭"
                  title="오늘의 브리핑 아이템이 없습니다"
                  description="관심기업의 새로운 소식이 있으면 업데이트됩니다."
                />
              )}
            </>
          ) : (
            <EmptyState
              icon="📋"
              title="오늘의 브리핑이 아직 준비되지 않았습니다"
              description="관심기업을 등록하면 매일 아침 브리핑을 받아볼 수 있습니다."
            />
          )}
        </>
      )}
    </div>
  );
}
