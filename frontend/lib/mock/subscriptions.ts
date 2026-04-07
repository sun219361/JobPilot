import type { Subscription } from "@/lib/types";

// 초기 구독 상태: 삼성전자(1), 카카오(5), 현대자동차(3)
export const MOCK_SUBSCRIPTIONS: Subscription[] = [
  {
    id: 1,
    company: {
      id: 1,
      name: "삼성전자",
      company_type: "LARGE",
      industry: "IT/전자",
      summary: "글로벌 반도체·스마트폰 선도기업. HBM, 파운드리, 모바일 부문 동시 성장 중.",
      homepage_url: "https://www.samsung.com/sec/",
      careers_url: "https://careers.samsung.com/",
      is_active: true,
    },
    memo: null,
    created_at: "2026-04-01T09:00:00Z",
  },
  {
    id: 2,
    company: {
      id: 5,
      name: "카카오",
      company_type: "LARGE",
      industry: "IT/플랫폼",
      summary: "국내 최대 모바일 플랫폼 기업. 메신저·핀테크·콘텐츠 서비스 다각화.",
      homepage_url: "https://www.kakaocorp.com",
      careers_url: "https://careers.kakao.com",
      is_active: true,
    },
    memo: null,
    created_at: "2026-04-02T10:30:00Z",
  },
  {
    id: 3,
    company: {
      id: 3,
      name: "현대자동차",
      company_type: "LARGE",
      industry: "자동차",
      summary: "국내 1위 완성차 기업. 전기차·수소차 전환 가속화 및 글로벌 시장 확대.",
      homepage_url: "https://www.hyundai.com",
      careers_url: "https://careers.hyundai.com",
      is_active: true,
    },
    memo: null,
    created_at: "2026-04-03T08:15:00Z",
  },
];
