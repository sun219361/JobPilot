import type { PrepSnapshot } from "@/lib/types";
import { SectionCard } from "@/components/common/SectionCard";
import { BulletPointList } from "@/components/companies/BulletPointList";
import { formatRelativeTime } from "@/lib/utils/format";

interface PrepSnapshotCardProps {
  snapshot: PrepSnapshot;
}

export function PrepSnapshotCard({ snapshot }: PrepSnapshotCardProps) {
  return (
    <div className="space-y-3">
      {/* 생성 시각 */}
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">준비 카드</p>
        <span className="text-xs text-gray-400">
          {formatRelativeTime(snapshot.generated_at)} 업데이트
        </span>
      </div>

      {/* 한 줄 요약 */}
      <div className="rounded-lg bg-blue-50 border border-blue-100 px-4 py-3">
        <p className="text-sm font-medium text-blue-800">{snapshot.one_line_summary}</p>
      </div>

      {/* 최근 이슈 */}
      <SectionCard title="📰 최근 이슈">
        <p className="text-sm text-gray-700 leading-relaxed">{snapshot.recent_issue_summary}</p>
      </SectionCard>

      {/* 채용 동향 */}
      <SectionCard title="💼 채용 동향">
        <p className="text-sm text-gray-700 leading-relaxed">{snapshot.hiring_summary}</p>
      </SectionCard>

      {/* 인재상 */}
      <SectionCard title="🎯 인재상">
        <p className="text-sm text-gray-700 leading-relaxed">{snapshot.talent_summary}</p>
      </SectionCard>

      {/* 자소서 포인트 */}
      <SectionCard title="✍️ 자소서 준비 포인트">
        <BulletPointList items={snapshot.cover_letter_points} />
      </SectionCard>

      {/* 면접 포인트 */}
      <SectionCard title="🗣️ 면접 준비 포인트">
        <BulletPointList items={snapshot.interview_points} />
      </SectionCard>
    </div>
  );
}
