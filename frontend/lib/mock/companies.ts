import type { Company, CompanyDetail, PrepSnapshot } from "@/lib/types";

export const MOCK_COMPANIES: Company[] = [
  {
    id: 1,
    name: "삼성전자",
    company_type: "LARGE",
    industry: "IT/전자",
    summary: "글로벌 반도체·스마트폰 선도기업. HBM, 파운드리, 모바일 부문 동시 성장 중.",
    homepage_url: "https://www.samsung.com/sec/",
    careers_url: "https://careers.samsung.com/",
    is_active: true,
  },
  {
    id: 2,
    name: "SK하이닉스",
    company_type: "LARGE",
    industry: "IT/반도체",
    summary: "세계 2위 메모리 반도체 기업. HBM3E 양산으로 AI 반도체 시장 선점.",
    homepage_url: "https://www.skhynix.com",
    careers_url: "https://recruit.skhynix.com",
    is_active: true,
  },
  {
    id: 3,
    name: "현대자동차",
    company_type: "LARGE",
    industry: "자동차",
    summary: "국내 1위 완성차 기업. 전기차·수소차 전환 가속화 및 글로벌 시장 확대.",
    homepage_url: "https://www.hyundai.com",
    careers_url: "https://careers.hyundai.com",
    is_active: true,
  },
  {
    id: 4,
    name: "LG전자",
    company_type: "LARGE",
    industry: "IT/전자",
    summary: "가전·B2B 솔루션·전장 부품 3대 축으로 성장 중인 글로벌 가전 기업.",
    homepage_url: "https://www.lge.co.kr",
    careers_url: "https://careers.lg.com",
    is_active: true,
  },
  {
    id: 5,
    name: "카카오",
    company_type: "LARGE",
    industry: "IT/플랫폼",
    summary: "국내 최대 모바일 플랫폼 기업. 메신저·핀테크·콘텐츠 서비스 다각화.",
    homepage_url: "https://www.kakaocorp.com",
    careers_url: "https://careers.kakao.com",
    is_active: true,
  },
  {
    id: 6,
    name: "네이버",
    company_type: "LARGE",
    industry: "IT/플랫폼",
    summary: "국내 1위 검색·커머스 플랫폼. 클라우드·AI·글로벌 웹툰 사업 확장.",
    homepage_url: "https://www.navercorp.com",
    careers_url: "https://recruit.navercorp.com",
    is_active: true,
  },
  {
    id: 7,
    name: "신한은행",
    company_type: "LARGE",
    industry: "금융/은행",
    summary: "국내 주요 시중은행. 디지털 뱅킹 전환 및 글로벌 금융 서비스 강화.",
    homepage_url: "https://www.shinhan.com",
    is_active: true,
  },
  {
    id: 8,
    name: "KB국민은행",
    company_type: "LARGE",
    industry: "금융/은행",
    summary: "국내 최대 은행 중 하나. 리브뱅크 디지털 뱅킹 플랫폼 서비스 운영.",
    is_active: true,
  },
  {
    id: 9,
    name: "넥슨",
    company_type: "MID",
    industry: "IT/게임",
    summary: "국내 최대 온라인 게임사. 메이플스토리·던전앤파이터 등 IP 기반 글로벌 확장.",
    homepage_url: "https://company.nexon.com",
    is_active: true,
  },
  {
    id: 10,
    name: "크래프톤",
    company_type: "MID",
    industry: "IT/게임",
    summary: "배틀그라운드 개발사. 인도·동남아 시장 집중 공략 및 AI 게임 기술 개발.",
    is_active: true,
  },
  {
    id: 11,
    name: "카카오뱅크",
    company_type: "MID",
    industry: "금융/핀테크",
    summary: "국내 1호 인터넷 전문은행. MAU 1800만 이상의 모바일 금융 플랫폼.",
    is_active: true,
  },
  {
    id: 12,
    name: "토스",
    company_type: "MID",
    industry: "금융/핀테크",
    summary: "비바리퍼블리카 운영. 간편송금 기반 종합 금융 슈퍼앱으로 성장.",
    is_active: true,
  },
  {
    id: 13,
    name: "무신사",
    company_type: "MID",
    industry: "패션/커머스",
    summary: "국내 최대 패션 플랫폼. 무신사스토어·무신사마켓 오프라인 확장 중.",
    is_active: true,
  },
  {
    id: 14,
    name: "한국전력공사",
    company_type: "PUBLIC",
    industry: "에너지/전력",
    summary: "국내 전력 공급 공기업. 재생에너지 전환 및 스마트그리드 구축 추진.",
    homepage_url: "https://home.kepco.co.kr",
    is_active: true,
  },
  {
    id: 15,
    name: "한국철도공사(코레일)",
    company_type: "PUBLIC",
    industry: "교통/물류",
    summary: "전국 철도 운영 공기업. KTX·SRT 운행 및 수도권 광역철도망 확대.",
    is_active: true,
  },
  {
    id: 16,
    name: "인천국제공항공사",
    company_type: "PUBLIC",
    industry: "교통/항공",
    summary: "인천공항 운영 공기업. 제2여객터미널 확장 및 스마트공항 전환 추진.",
    is_active: true,
  },
  {
    id: 17,
    name: "한국수력원자력",
    company_type: "PUBLIC",
    industry: "에너지/원자력",
    summary: "원자력·수력 발전 공기업. SMR 개발 및 원전 해외 수출 추진.",
    is_active: true,
  },
  {
    id: 18,
    name: "쏘카",
    company_type: "MID",
    industry: "모빌리티",
    summary: "국내 1위 카셰어링 기업. 전기차 전환 및 B2B 플릿 서비스 확장.",
    is_active: true,
  },
  {
    id: 19,
    name: "야놀자",
    company_type: "MID",
    industry: "여행/플랫폼",
    summary: "글로벌 여가 플랫폼. 인터파크 인수 후 여행·레저 통합 서비스 운영.",
    is_active: true,
  },
  {
    id: 20,
    name: "국민건강보험공단",
    company_type: "PUBLIC",
    industry: "보건/의료",
    summary: "건강보험 운영 공단. 빅데이터 기반 건강관리 서비스 디지털화 추진.",
    is_active: true,
  },
];

const MOCK_PREP_SNAPSHOTS: Record<number, PrepSnapshot> = {
  1: {
    id: 101,
    one_line_summary: "AI·반도체 핵심 역량을 보유한 글로벌 1위 종합 전자 기업",
    recent_issue_summary:
      "HBM4 양산 임박 및 파운드리 수주 확대. 갤럭시 AI 기능으로 스마트폰 차별화. 2024년 DS부문 영업이익 회복세.",
    hiring_summary:
      "DS·DX 양대 부문 중심으로 채용 진행. 소프트웨어·AI 직군 비중 전년 대비 증가. 상반기 신입 공채 예정.",
    talent_summary:
      "창의와 혁신을 강조하는 '삼성인' 인재상. 최근 AI·SW 역량 보유자 우대 경향 뚜렷. 도전 정신과 글로벌 마인드 핵심.",
    cover_letter_points: [
      "지원 직무와 연계된 프로젝트 경험을 구체적 수치로 제시 (예: 성능 X% 개선)",
      "AI·반도체·소프트웨어 키워드를 자연스럽게 녹여 직무 연관성 어필",
      "삼성의 3대 가치(인재, 기술, 사회공헌)와 본인 가치관 연결",
      "글로벌 협업 경험 또는 외국어 역량 구체적으로 언급",
    ],
    interview_points: [
      "GSAT(직무적성검사) 수리·추리 영역 집중 준비 필수",
      "지원 직무의 최신 기술 트렌드(HBM, 온디바이스AI 등) 사전 숙지",
      "인성 면접: '실패 경험과 극복 과정'을 STAR 기법으로 준비",
      "직무 면접: 전공 기초 지식과 실무 적용 사례 정리",
    ],
    generated_at: "2026-04-06T06:00:00Z",
  },
  5: {
    id: 102,
    one_line_summary: "5,000만 국민 메신저 기반의 모바일 라이프 플랫폼 기업",
    recent_issue_summary:
      "카카오톡 광고 매출 회복세. AI 서비스 카나나 출시 준비 중. 핀테크·콘텐츠 자회사 수익성 개선 집중.",
    hiring_summary:
      "플랫폼 개발·데이터 분석·AI 직군 상시 채용. 경력 우대 경향이나 우수 신입도 적극 채용 중.",
    talent_summary:
      "자율과 책임 중심의 수평적 조직문화. 문제해결 능력과 데이터 기반 사고를 가장 중시. 빠른 실행력과 협업 역량 강조.",
    cover_letter_points: [
      "카카오 서비스(카카오톡, 카카오페이 등) 실제 사용 경험 기반 개선 아이디어 제시",
      "데이터 기반으로 문제를 정의하고 해결한 경험 구체화",
      "자율적으로 목표를 설정하고 달성한 경험 강조",
      "협업 시 발생한 갈등 해결 방식과 그 결과 서술",
    ],
    interview_points: [
      "카카오 서비스 최근 개편 사항 및 경쟁사 동향 파악 필수",
      "코딩 테스트: 알고리즘·자료구조 중심, 프로그래머스 기출 다수 풀이 권장",
      "직무 면접: '이 기능을 어떻게 개선할 것인가' 류 프로덕트 감각 질문 빈번",
      "컬처 핏: 수평적 문화에서의 주도적 행동 경험 사례 준비",
    ],
    generated_at: "2026-04-06T06:00:00Z",
  },
  3: {
    id: 103,
    one_line_summary: "전동화·SDV 전환을 가속화하는 글로벌 완성차 그룹",
    recent_issue_summary:
      "아이오닉6 글로벌 수상 및 북미 판매 호조. 로보틱스·UAM 미래 사업 투자 확대. 소프트웨어 정의 자동차(SDV) 전환 선언.",
    hiring_summary:
      "연구개발·전동화·소프트웨어 직군 채용 비중 확대. 기계·전기전자·컴퓨터 전공 선호. 상반기 대규모 공채 진행.",
    talent_summary:
      "도전·소통·협력의 현대차 인재상. 최근 SDV 전환으로 소프트웨어·AI 역량 보유자 우대. 글로벌 감각과 능동성 중시.",
    cover_letter_points: [
      "자동차 산업 전동화·SDV 트렌드와 지원 직무 연결 필수",
      "현대차의 미래 사업(AAM, 로보틱스, SDV)에 대한 관심과 기여 방향 명시",
      "팀 프로젝트에서의 리더십 또는 팔로워십 경험 구체화",
      "해외 경험·외국어 역량 보유자는 반드시 언급",
    ],
    interview_points: [
      "인·적성 검사(HMAT) 언어·수리·공간지각 영역 준비 필요",
      "전동화·수소차 기술 기초(배터리 구조, 수소연료전지 원리) 숙지",
      "직무 면접: 제조 공정 최적화, 품질 관리 등 실무 지식 질문 빈번",
      "글로벌 비즈니스 환경에서의 커뮤니케이션 역량 강조",
    ],
    generated_at: "2026-04-06T06:00:00Z",
  },
  6: {
    id: 104,
    one_line_summary: "AI·클라우드·글로벌 콘텐츠로 도약하는 국내 1위 IT 기업",
    recent_issue_summary:
      "하이퍼클로바X AI 서비스 기업 고객 확대. 웹툰 글로벌 1위 유지. 클라우드 사업 B2B 시장 점유율 성장 중.",
    hiring_summary:
      "AI 연구·클라우드 엔지니어링·데이터 분석 직군 집중 채용. 직무 중심 수시 채용이 주를 이루며 공채 병행.",
    talent_summary:
      "탁월함·성장·신뢰 중심의 NAVER 인재상. 기술적 전문성과 함께 서비스 임팩트에 집중하는 역량을 중시. 자기주도성 최우선.",
    cover_letter_points: [
      "네이버 서비스(검색, 스마트스토어, 클라우드 등) 실제 개선 경험 또는 아이디어 제시",
      "AI·ML·데이터 관련 프로젝트 경험 수치화하여 임팩트 강조",
      "자기주도 학습 및 프로젝트 진행 방식 구체적으로 서술",
      "글로벌 서비스 확장(라인, 웹툰)에 기여할 역량 어필",
    ],
    interview_points: [
      "코딩 테스트: 알고리즘 구현, 시스템 설계 문제 중심",
      "AI/ML 직군: 논문 리뷰 및 모델 설계 경험 사전 정리 필수",
      "직무 면접: 실제 서비스 장애 대응, 성능 최적화 경험 질문 빈번",
      "인성 면접: 본인 강점을 네이버 서비스 발전에 어떻게 적용할지 구체화",
    ],
    generated_at: "2026-04-06T06:00:00Z",
  },
  14: {
    id: 105,
    one_line_summary: "에너지 전환을 이끄는 국내 최대 전력 공급 공기업",
    recent_issue_summary:
      "재생에너지 비중 확대 목표 선언. 스마트그리드 2단계 사업 착수. ESG 경영 강화로 친환경 에너지 인프라 구축 가속화.",
    hiring_summary:
      "전기·기계·ICT 직군 NCS 기반 공개 채용. 블라인드 채용 원칙. 채용형 인턴 후 정규직 전환 비율 높음.",
    talent_summary:
      "공공성과 전문성을 겸비한 인재상. NCS 직업기초능력 평가 중심. 에너지 분야 전문 지식과 공직 윤리의식 강조.",
    cover_letter_points: [
      "에너지 산업 트렌드(재생에너지, ESG)와 지원 직무 연결 필수",
      "NCS 기반 직무 역량 기술서를 꼼꼼히 읽고 경험 매핑",
      "공공기관 특성상 팀워크와 공공 가치 실현 경험 강조",
      "관련 자격증(전기기사, 기술사 등) 보유 시 반드시 언급",
    ],
    interview_points: [
      "NCS 직업기초능력평가 의사소통·수리·문제해결 영역 집중",
      "전력 시스템 기초 지식(송배전, 변전 등) 숙지 필수",
      "PT 면접: 에너지 정책 현안에 대한 의견 논리적 제시 준비",
      "직무 면접: 안전·환경 관련 이슈 대응 경험 사례 정리",
    ],
    generated_at: "2026-04-06T06:00:00Z",
  },
};

export function getMockCompanyDetail(id: number): CompanyDetail | null {
  const company = MOCK_COMPANIES.find((c) => c.id === id);
  if (!company) return null;
  return {
    ...company,
    latest_prep_snapshot: MOCK_PREP_SNAPSHOTS[id] ?? null,
  };
}
