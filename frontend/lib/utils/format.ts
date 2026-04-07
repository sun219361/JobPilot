import type { CompanyType, SourceType } from "@/lib/types";

// 기업 유형 표시 텍스트
export const COMPANY_TYPE_LABEL: Record<CompanyType, string> = {
  LARGE: "대기업",
  MID: "중견기업",
  PUBLIC: "공기업",
};

// 기업 유형 색상 (Tailwind)
export const COMPANY_TYPE_COLOR: Record<CompanyType, string> = {
  LARGE: "bg-blue-50 text-blue-700 border-blue-200",
  MID: "bg-violet-50 text-violet-700 border-violet-200",
  PUBLIC: "bg-emerald-50 text-emerald-700 border-emerald-200",
};

// 소스 타입 표시 텍스트
export const SOURCE_TYPE_LABEL: Record<SourceType, string> = {
  news: "뉴스",
  job: "채용",
  notice: "공지",
};

// 소스 타입 색상
export const SOURCE_TYPE_COLOR: Record<SourceType, string> = {
  news: "bg-sky-50 text-sky-700 border-sky-200",
  job: "bg-orange-50 text-orange-700 border-orange-200",
  notice: "bg-gray-50 text-gray-600 border-gray-200",
};

// 날짜 포맷: "2026-04-06" → "2026년 4월 6일 (일)"
export function formatDate(dateStr: string): string {
  const d = new Date(dateStr);
  const year = d.getFullYear();
  const month = d.getMonth() + 1;
  const day = d.getDate();
  const weekDays = ["일", "월", "화", "수", "목", "금", "토"];
  const weekDay = weekDays[d.getDay()];
  return `${year}년 ${month}월 ${day}일 (${weekDay})`;
}

// 상대 시간: "3시간 전" 등
export function formatRelativeTime(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return "방금 전";
  if (minutes < 60) return `${minutes}분 전`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}시간 전`;
  const days = Math.floor(hours / 24);
  return `${days}일 전`;
}
