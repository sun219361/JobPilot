import type { CompanyType, SourceType } from "@/lib/types";
import { COMPANY_TYPE_LABEL, COMPANY_TYPE_COLOR, SOURCE_TYPE_LABEL, SOURCE_TYPE_COLOR } from "@/lib/utils/format";

// ─────────────────────────────────────────────
// CompanyTypeBadge
// ─────────────────────────────────────────────

interface CompanyTypeBadgeProps {
  type: CompanyType;
  size?: "sm" | "md";
}

export function CompanyTypeBadge({ type, size = "md" }: CompanyTypeBadgeProps) {
  const sizeClass = size === "sm" ? "text-xs px-1.5 py-0.5" : "text-xs px-2 py-1";
  return (
    <span
      className={`inline-flex items-center rounded border font-medium ${sizeClass} ${COMPANY_TYPE_COLOR[type]}`}
    >
      {COMPANY_TYPE_LABEL[type]}
    </span>
  );
}

// ─────────────────────────────────────────────
// SourceTypeBadge
// ─────────────────────────────────────────────

interface SourceTypeBadgeProps {
  type: SourceType;
}

export function SourceTypeBadge({ type }: SourceTypeBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded border text-xs font-medium px-1.5 py-0.5 ${SOURCE_TYPE_COLOR[type]}`}
    >
      {SOURCE_TYPE_LABEL[type]}
    </span>
  );
}
