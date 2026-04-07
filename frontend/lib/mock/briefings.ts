import type { TodayBriefingResponse } from "@/lib/types";

const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD

export const MOCK_TODAY_BRIEFING: TodayBriefingResponse = {
  briefing: {
    id: 1,
    briefing_date: today,
    title: `${today.replace(/-/g, "년 ").replace(/-/, "월 ")}일 관심기업 브리핑`,
    created_at: `${today}T06:00:00Z`,
  },
  items: [
    {
      id: 1,
      company_id: 1,
      company_name: "삼성전자",
      source_type: "news",
      headline: "삼성전자, HBM4 4분기 양산 공식 확인",
      summary:
        "삼성전자가 2024년 4분기 내 HBM4 양산을 시작한다고 공식 발표. 엔비디아 차세대 블랙웰 GPU 탑재 유력.",
      action_point: "반도체 직군 지원자라면 HBM 구조와 삼성 DS부문 전략 숙지 필수.",
      sort_order: 1,
    },
    {
      id: 2,
      company_id: 1,
      company_name: "삼성전자",
      source_type: "job",
      headline: "[마감 D-14] 삼성전자 2024 상반기 DS부문 신입사원 공채",
      summary:
        "반도체 설계·공정 직군 중심. 학사 이상, GSAT 필기 전형 포함. 지원 마감: 2024-02-29.",
      action_point:
        "GSAT 준비 병행 필수. 직무 기술서 꼼꼼히 읽고 경험과 매칭하여 자소서 작성 권장.",
      sort_order: 2,
    },
    {
      id: 3,
      company_id: 3,
      company_name: "현대자동차",
      source_type: "news",
      headline: "현대차, 미국 조지아 전기차 공장 가동 개시",
      summary:
        "현대차 메타플랜트 아메리카(HMGMA)가 아이오닉5 생산을 시작. 연간 30만대 생산 목표.",
      action_point:
        "전동화·해외 생산 전략 관련 면접 질문 대비. 아이오닉 라인업 숙지 권장.",
      sort_order: 3,
    },
    {
      id: 4,
      company_id: 3,
      company_name: "현대자동차",
      source_type: "job",
      headline: "현대자동차 2024 상반기 연구개발 직군 공채",
      summary:
        "전동화·SDV·로보틱스 R&D 직군 채용. 기계·전기전자·컴퓨터 전공 우대. HMAT 전형 포함.",
      action_point:
        "SDV(소프트웨어 정의 자동차) 관련 프로젝트 경험 자소서에 강조. 포트폴리오 준비 권장.",
      sort_order: 4,
    },
    {
      id: 5,
      company_id: 5,
      company_name: "카카오",
      source_type: "news",
      headline: "카카오, AI 어시스턴트 '카나나' 베타 서비스 시작",
      summary:
        "카카오가 자체 개발 LLM 기반 AI 서비스 카나나 베타를 출시. 카카오톡 연동 개인화 서비스 제공.",
      action_point: "카카오 AI 전략과 서비스 사용 경험을 면접 시 적극 활용 권장.",
      sort_order: 5,
    },
    {
      id: 6,
      company_id: 5,
      company_name: "카카오",
      source_type: "news",
      headline: "카카오페이, 해외 결제 서비스 동남아 3개국 확장",
      summary:
        "카카오페이가 태국·베트남·인도네시아에서 QR 결제 서비스를 개시. 글로벌 핀테크 시장 공략 가속화.",
      action_point: "카카오 핀테크 사업 확장 전략 숙지. 글로벌 관심 어필 기회 활용.",
      sort_order: 6,
    },
  ],
};
