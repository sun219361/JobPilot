import Link from "next/link";
import type { BriefingItem } from "@/lib/types";
import { SourceTypeBadge } from "@/components/common/Badge";

interface BriefingItemCardProps {
  item: BriefingItem;
}

export function BriefingItemCard({ item }: BriefingItemCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 hover:border-gray-300 transition-colors">
      {/* 상단: 배지 + 기업명 */}
      <div className="flex items-center gap-2 flex-wrap mb-2">
        <SourceTypeBadge type={item.source_type} />
        {item.company_id && item.company_name ? (
          <Link
            href={`/companies/${item.company_id}`}
            className="text-xs font-medium text-gray-600 hover:text-blue-600 transition-colors"
          >
            {item.company_name}
          </Link>
        ) : (
          item.company_name && (
            <span className="text-xs font-medium text-gray-500">{item.company_name}</span>
          )
        )}
      </div>

      {/* 헤드라인 */}
      <p className="text-sm font-semibold text-gray-900 leading-snug mb-1.5">
        {item.headline}
      </p>

      {/* 요약 */}
      <p className="text-sm text-gray-600 leading-relaxed">{item.summary}</p>

      {/* 액션 포인트 */}
      {item.action_point && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <div className="flex items-start gap-2">
            <span className="flex-shrink-0 mt-0.5 text-xs font-semibold text-amber-600 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded">
              포인트
            </span>
            <p className="text-xs text-gray-600 leading-relaxed">{item.action_point}</p>
          </div>
        </div>
      )}
    </div>
  );
}
