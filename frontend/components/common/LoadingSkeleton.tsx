// ─────────────────────────────────────────────
// LoadingSkeleton
// ─────────────────────────────────────────────

interface SkeletonProps {
  className?: string;
}

function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div className={`animate-pulse rounded bg-gray-200 ${className}`} />
  );
}

// 기업 카드 skeleton
export function CompanyCardSkeleton() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="space-y-2 flex-1">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-20" />
        </div>
        <Skeleton className="h-8 w-8 rounded" />
      </div>
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-3/4" />
    </div>
  );
}

// 브리핑 카드 skeleton
export function BriefingItemSkeleton() {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Skeleton className="h-5 w-12" />
        <Skeleton className="h-4 w-24" />
      </div>
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-4/5" />
      <div className="pt-1 border-t border-gray-100">
        <Skeleton className="h-3 w-3/4" />
      </div>
    </div>
  );
}

// 기업 상세 skeleton
export function CompanyDetailSkeleton() {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
        <Skeleton className="h-6 w-40" />
        <div className="flex gap-2">
          <Skeleton className="h-5 w-16" />
          <Skeleton className="h-5 w-20" />
        </div>
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
        <Skeleton className="h-5 w-28" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-5/6" />
        <Skeleton className="h-3 w-4/5" />
      </div>
      <div className="rounded-lg border border-gray-200 bg-white p-5 space-y-3">
        <Skeleton className="h-5 w-28" />
        {[1, 2, 3].map((i) => (
          <div key={i} className="flex gap-2">
            <Skeleton className="h-3 w-3 mt-0.5 flex-shrink-0" />
            <Skeleton className="h-3 flex-1" />
          </div>
        ))}
      </div>
    </div>
  );
}

// 리스트 skeleton (n개)
export function ListSkeleton({ count = 3, Item }: { count?: number; Item: React.FC }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <Item key={i} />
      ))}
    </div>
  );
}
