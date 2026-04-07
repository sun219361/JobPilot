"""
seed.py — 로컬 개발용 초기 데이터 삽입 스크립트

실행 방법:
  cd backend
  python -m app.scripts.seed

주의: 중복 실행 시 기존 데이터를 삭제 후 재삽입한다.
"""

import sys
import os
from datetime import datetime, date, timezone

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.core.db import SessionLocal
from app.models import User, Company, CompanyType, Subscription, PrepSnapshot, Briefing, BriefingItem


def run_seed():
    db = SessionLocal()
    try:
        print("🌱 기존 데이터 초기화 중...")
        db.query(BriefingItem).delete()
        db.query(Briefing).delete()
        db.query(PrepSnapshot).delete()
        db.query(Subscription).delete()
        db.query(Company).delete()
        db.query(User).delete()
        db.commit()

        # ── 1. 테스트 유저 ────────────────────────────────
        print("👤 유저 생성 중...")
        user = User(id=1, email="dev@jobpilot.kr", nickname="개발자")
        db.add(user)
        db.flush()

        # ── 2. 기업 30개 ──────────────────────────────────
        print("🏢 기업 데이터 생성 중...")
        companies_data = [
            # 대기업 (LARGE) - 10개
            {"name": "삼성전자", "company_type": CompanyType.LARGE, "industry": "IT/전자", "summary": "글로벌 반도체·스마트폰 선도기업. HBM, 파운드리, 모바일 부문 동시 성장 중.", "homepage_url": "https://www.samsung.com/sec/", "careers_url": "https://careers.samsung.com/"},
            {"name": "SK하이닉스", "company_type": CompanyType.LARGE, "industry": "IT/반도체", "summary": "세계 2위 메모리 반도체 기업. HBM3E 양산으로 AI 반도체 시장 선점.", "homepage_url": "https://www.skhynix.com", "careers_url": "https://recruit.skhynix.com"},
            {"name": "현대자동차", "company_type": CompanyType.LARGE, "industry": "자동차", "summary": "국내 1위 완성차 기업. 전기차·수소차 전환 가속화 및 글로벌 시장 확대.", "homepage_url": "https://www.hyundai.com", "careers_url": "https://careers.hyundai.com"},
            {"name": "LG전자", "company_type": CompanyType.LARGE, "industry": "IT/전자", "summary": "가전·B2B 솔루션·전장 부품 3대 축으로 성장 중인 글로벌 가전 기업.", "homepage_url": "https://www.lge.co.kr", "careers_url": "https://careers.lg.com"},
            {"name": "카카오", "company_type": CompanyType.LARGE, "industry": "IT/플랫폼", "summary": "국내 최대 모바일 플랫폼 기업. 메신저·핀테크·콘텐츠 서비스 다각화.", "homepage_url": "https://www.kakaocorp.com", "careers_url": "https://careers.kakao.com"},
            {"name": "네이버", "company_type": CompanyType.LARGE, "industry": "IT/플랫폼", "summary": "국내 1위 검색·커머스 플랫폼. 클라우드·AI·글로벌 웹툰 사업 확장.", "homepage_url": "https://www.navercorp.com", "careers_url": "https://recruit.navercorp.com"},
            {"name": "신한은행", "company_type": CompanyType.LARGE, "industry": "금융/은행", "summary": "국내 주요 시중은행. 디지털 뱅킹 전환 및 글로벌 금융 서비스 강화.", "homepage_url": "https://www.shinhan.com", "careers_url": "https://shinhan.recruiter.co.kr"},
            {"name": "KB국민은행", "company_type": CompanyType.LARGE, "industry": "금융/은행", "summary": "국내 최대 은행 중 하나. 리브뱅크 디지털 뱅킹 플랫폼 서비스 운영.", "homepage_url": "https://www.kbstar.com", "careers_url": "https://kbstar.recruiter.co.kr"},
            {"name": "삼성물산", "company_type": CompanyType.LARGE, "industry": "건설/유통", "summary": "삼성그룹 지주사 역할의 건설·상사·패션 복합 기업.", "homepage_url": "https://www.samsungcnt.com", "careers_url": "https://www.samsungcnt.com/career"},
            {"name": "CJ제일제당", "company_type": CompanyType.LARGE, "industry": "식품/바이오", "summary": "K-Food 글로벌화 선도. 비비고 브랜드를 중심으로 해외 시장 빠르게 성장 중.", "homepage_url": "https://www.cj.co.kr", "careers_url": "https://recruit.cj.net"},

            # 중견기업 (MID) - 10개
            {"name": "넥슨", "company_type": CompanyType.MID, "industry": "IT/게임", "summary": "국내 최대 온라인 게임사. 메이플스토리·던전앤파이터 등 IP 기반 글로벌 확장.", "homepage_url": "https://company.nexon.com", "careers_url": "https://company.nexon.com/ko/recruit"},
            {"name": "크래프톤", "company_type": CompanyType.MID, "industry": "IT/게임", "summary": "배틀그라운드 개발사. 인도·동남아 시장 집중 공략 및 AI 게임 기술 개발.", "homepage_url": "https://www.krafton.com", "careers_url": "https://krafton.com/careers"},
            {"name": "한화시스템", "company_type": CompanyType.MID, "industry": "방산/IT", "summary": "방산 IT 전문 기업. UAM·위성통신 등 미래 첨단 방산 분야 투자 확대.", "homepage_url": "https://www.hanwhasystems.com", "careers_url": "https://hanwhasystems.recruiter.co.kr"},
            {"name": "카카오뱅크", "company_type": CompanyType.MID, "industry": "금융/핀테크", "summary": "국내 1호 인터넷 전문은행. MAU 1800만 이상의 모바일 금융 플랫폼.", "homepage_url": "https://www.kakaobank.com", "careers_url": "https://kakaobank.com/career"},
            {"name": "토스", "company_type": CompanyType.MID, "industry": "금융/핀테크", "summary": "비바리퍼블리카 운영. 간편송금 기반 종합 금융 슈퍼앱으로 성장.", "homepage_url": "https://toss.im", "careers_url": "https://toss.im/career"},
            {"name": "무신사", "company_type": CompanyType.MID, "industry": "패션/커머스", "summary": "국내 최대 패션 플랫폼. 무신사스토어·무신사마켓 오프라인 확장 중.", "homepage_url": "https://www.musinsa.com", "careers_url": "https://career.musinsa.com"},
            {"name": "컬리", "company_type": CompanyType.MID, "industry": "이커머스/식품", "summary": "새벽배송 개척 기업. 마켓컬리 운영. 뷰티컬리로 뷰티 카테고리 확장.", "homepage_url": "https://company.kurly.com", "careers_url": "https://careers.kurly.com"},
            {"name": "쏘카", "company_type": CompanyType.MID, "industry": "모빌리티", "summary": "국내 1위 카셰어링 기업. 전기차 전환 및 B2B 플릿 서비스 확장.", "homepage_url": "https://www.socar.kr", "careers_url": "https://socar.kr/career"},
            {"name": "야놀자", "company_type": CompanyType.MID, "industry": "여행/플랫폼", "summary": "글로벌 여가 플랫폼. 인터파크 인수 후 여행·레저 통합 서비스 운영.", "homepage_url": "https://www.yanolja.com", "careers_url": "https://careers.yanolja.co"},
            {"name": "오리온", "company_type": CompanyType.MID, "industry": "식품", "summary": "국내 대표 제과 기업. 초코파이 중심 중국·베트남·러시아 등 글로벌 성장.", "homepage_url": "https://www.orion.com", "careers_url": "https://recruit.orionworld.com"},

            # 공기업 (PUBLIC) - 10개
            {"name": "한국전력공사", "company_type": CompanyType.PUBLIC, "industry": "에너지/전력", "summary": "국내 전력 공급 공기업. 재생에너지 전환 및 스마트그리드 구축 추진.", "homepage_url": "https://home.kepco.co.kr", "careers_url": "https://kepco.recruiter.co.kr"},
            {"name": "한국철도공사(코레일)", "company_type": CompanyType.PUBLIC, "industry": "교통/물류", "summary": "전국 철도 운영 공기업. KTX·SRT 운행 및 수도권 광역철도망 확대.", "homepage_url": "https://www.korail.com", "careers_url": "https://korail.recruiter.co.kr"},
            {"name": "한국수자원공사", "company_type": CompanyType.PUBLIC, "industry": "환경/수자원", "summary": "수자원 개발 및 수도 서비스 공기업. 스마트 물관리 인프라 구축 중.", "homepage_url": "https://www.kwater.or.kr", "careers_url": "https://kwater.recruiter.co.kr"},
            {"name": "한국토지주택공사(LH)", "company_type": CompanyType.PUBLIC, "industry": "건설/부동산", "summary": "주택·도시 개발 공기업. 3기 신도시 사업 및 공공임대주택 공급 확대.", "homepage_url": "https://www.lh.or.kr", "careers_url": "https://lh.recruiter.co.kr"},
            {"name": "국민건강보험공단", "company_type": CompanyType.PUBLIC, "industry": "보건/의료", "summary": "건강보험 운영 공단. 빅데이터 기반 건강관리 서비스 디지털화 추진.", "homepage_url": "https://www.nhis.or.kr", "careers_url": "https://nhis.recruiter.co.kr"},
            {"name": "국민연금공단", "company_type": CompanyType.PUBLIC, "industry": "연금/복지", "summary": "국가 연금 운영 공단. ESG 투자 확대 및 기금운용 수익률 개선 목표.", "homepage_url": "https://www.nps.or.kr", "careers_url": "https://nps.recruiter.co.kr"},
            {"name": "인천국제공항공사", "company_type": CompanyType.PUBLIC, "industry": "교통/항공", "summary": "인천공항 운영 공기업. 제2여객터미널 확장 및 스마트공항 전환 추진.", "homepage_url": "https://www.airport.kr", "careers_url": "https://airport.recruiter.co.kr"},
            {"name": "한국도로공사", "company_type": CompanyType.PUBLIC, "industry": "교통/인프라", "summary": "고속도로 건설·관리 공기업. 자율주행 인프라 및 스마트 톨링 시스템 구축.", "homepage_url": "https://www.ex.co.kr", "careers_url": "https://ex.recruiter.co.kr"},
            {"name": "한국가스공사", "company_type": CompanyType.PUBLIC, "industry": "에너지/가스", "summary": "천연가스 도입·공급 공기업. 수소 에너지 전환 및 해외 자원개발 투자.", "homepage_url": "https://www.kogas.or.kr", "careers_url": "https://kogas.recruiter.co.kr"},
            {"name": "한국수력원자력", "company_type": CompanyType.PUBLIC, "industry": "에너지/원자력", "summary": "원자력·수력 발전 공기업. SMR 개발 및 원전 해외 수출 추진.", "homepage_url": "https://www.khnp.co.kr", "careers_url": "https://khnp.recruiter.co.kr"},
        ]

        company_objects = []
        for data in companies_data:
            c = Company(**data)
            db.add(c)
            company_objects.append(c)
        db.flush()

        print(f"  ✅ 기업 {len(company_objects)}개 생성 완료")

        # ── 3. PrepSnapshot (대기업 5개) ──────────────────
        print("📋 준비 카드 스냅샷 생성 중...")
        now = datetime.now(tz=timezone.utc)

        prep_data = [
            {
                "company_name": "삼성전자",
                "one_line_summary": "AI·반도체 핵심 역량을 보유한 글로벌 1위 종합 전자 기업",
                "recent_issue_summary": "HBM4 양산 임박 및 파운드리 수주 확대. 갤럭시 AI 기능으로 스마트폰 차별화. 2024년 DS부문 영업이익 회복세.",
                "hiring_summary": "DS·DX 양대 부문 중심으로 채용 진행. 소프트웨어·AI 직군 비중 전년 대비 증가. 상반기 신입 공채 예정.",
                "talent_summary": "창의와 혁신을 강조하는 '삼성인' 인재상. 최근 AI·SW 역량 보유자 우대 경향 뚜렷. 도전 정신과 글로벌 마인드 핵심.",
                "cover_letter_points": [
                    "지원 직무와 연계된 프로젝트 경험을 구체적 수치로 제시 (예: 성능 X% 개선)",
                    "AI·반도체·소프트웨어 키워드를 자연스럽게 녹여 직무 연관성 어필",
                    "삼성의 3대 가치(인재, 기술, 사회공헌)와 본인 가치관 연결",
                    "글로벌 협업 경험 또는 외국어 역량 구체적으로 언급",
                ],
                "interview_points": [
                    "GSAT(직무적성검사) 수리·추리 영역 집중 준비 필수",
                    "지원 직무의 최신 기술 트렌드(HBM, 온디바이스AI 등) 사전 숙지",
                    "인성 면접: '실패 경험과 극복 과정'을 STAR 기법으로 준비",
                    "직무 면접: 전공 기초 지식과 실무 적용 사례 정리",
                ],
            },
            {
                "company_name": "카카오",
                "one_line_summary": "5,000만 국민 메신저 기반의 모바일 라이프 플랫폼 기업",
                "recent_issue_summary": "카카오톡 광고 매출 회복세. AI 서비스 카나나 출시 준비 중. 핀테크·콘텐츠 자회사 수익성 개선 집중.",
                "hiring_summary": "플랫폼 개발·데이터 분석·AI 직군 상시 채용. 경력 우대 경향이나 우수 신입도 적극 채용 중.",
                "talent_summary": "자율과 책임 중심의 수평적 조직문화. 문제해결 능력과 데이터 기반 사고를 가장 중시. 빠른 실행력과 협업 역량 강조.",
                "cover_letter_points": [
                    "카카오 서비스(카카오톡, 카카오페이 등) 실제 사용 경험 기반 개선 아이디어 제시",
                    "데이터 기반으로 문제를 정의하고 해결한 경험 구체화",
                    "자율적으로 목표를 설정하고 달성한 경험 강조",
                    "협업 시 발생한 갈등 해결 방식과 그 결과 서술",
                ],
                "interview_points": [
                    "카카오 서비스 최근 개편 사항 및 경쟁사 동향 파악 필수",
                    "코딩 테스트: 알고리즘·자료구조 중심, 프로그래머스 기출 다수 풀이 권장",
                    "직무 면접: '이 기능을 어떻게 개선할 것인가' 류 프로덕트 감각 질문 빈번",
                    "컬처 핏: 수평적 문화에서의 주도적 행동 경험 사례 준비",
                ],
            },
            {
                "company_name": "현대자동차",
                "one_line_summary": "전동화·SDV 전환을 가속화하는 글로벌 완성차 그룹",
                "recent_issue_summary": "아이오닉6 글로벌 수상 및 북미 판매 호조. 로보틱스·UAM 미래 사업 투자 확대. 소프트웨어 정의 자동차(SDV) 전환 선언.",
                "hiring_summary": "연구개발·전동화·소프트웨어 직군 채용 비중 확대. 기계·전기전자·컴퓨터 전공 선호. 상반기 대규모 공채 진행.",
                "talent_summary": "도전·소통·협력의 현대차 인재상. 최근 SDV 전환으로 소프트웨어·AI 역량 보유자 우대. 글로벌 감각과 능동성 중시.",
                "cover_letter_points": [
                    "자동차 산업 전동화·SDV 트렌드와 지원 직무 연결 필수",
                    "현대차의 미래 사업(AAM, 로보틱스, SDV)에 대한 관심과 기여 방향 명시",
                    "팀 프로젝트에서의 리더십 또는 팔로워십 경험 구체화",
                    "해외 경험·외국어 역량 보유자는 반드시 언급",
                ],
                "interview_points": [
                    "인·적성 검사(HMAT) 언어·수리·공간지각 영역 준비 필요",
                    "전동화·수소차 기술 기초(배터리 구조, 수소연료전지 원리) 숙지",
                    "직무 면접: 제조 공정 최적화, 품질 관리 등 실무 지식 질문 빈번",
                    "글로벌 비즈니스 환경에서의 커뮤니케이션 역량 강조",
                ],
            },
            {
                "company_name": "네이버",
                "one_line_summary": "AI·클라우드·글로벌 콘텐츠로 도약하는 국내 1위 IT 기업",
                "recent_issue_summary": "하이퍼클로바X AI 서비스 기업 고객 확대. 웹툰 글로벌 1위 유지. 클라우드 사업 B2B 시장 점유율 성장 중.",
                "hiring_summary": "AI 연구·클라우드 엔지니어링·데이터 분석 직군 집중 채용. 직무 중심 수시 채용이 주를 이루며 공채 병행.",
                "talent_summary": "탁월함·성장·신뢰 중심의 NAVER 인재상. 기술적 전문성과 함께 서비스 임팩트에 집중하는 역량을 중시. 자기주도성 최우선.",
                "cover_letter_points": [
                    "네이버 서비스(검색, 스마트스토어, 클라우드 등) 실제 개선 경험 또는 아이디어 제시",
                    "AI·ML·데이터 관련 프로젝트 경험 수치화하여 임팩트 강조",
                    "자기주도 학습 및 프로젝트 진행 방식 구체적으로 서술",
                    "글로벌 서비스 확장(라인, 웹툰)에 기여할 역량 어필",
                ],
                "interview_points": [
                    "코딩 테스트: 알고리즘 구현, 시스템 설계 문제 중심",
                    "AI/ML 직군: 논문 리뷰 및 모델 설계 경험 사전 정리 필수",
                    "직무 면접: 실제 서비스 장애 대응, 성능 최적화 경험 질문 빈번",
                    "인성 면접: 본인 강점을 네이버 서비스 발전에 어떻게 적용할지 구체화",
                ],
            },
            {
                "company_name": "신한은행",
                "one_line_summary": "디지털 혁신을 선도하는 국내 대표 시중은행",
                "recent_issue_summary": "쏠(SOL) 앱 MAU 1000만 돌파. AI 기반 여신 심사 시스템 전환. ESG 금융 상품 출시 확대.",
                "hiring_summary": "디지털·ICT 직군 채용 비중 확대 추세. 일반직·ICT직 구분 공채 진행. 금융공학·데이터 분석 우대.",
                "talent_summary": "신한 Way(열정·헌신·팀워크) 중심 인재상. 디지털 금융 전환에 발맞춰 데이터 리터러시와 핀테크 이해도 우대.",
                "cover_letter_points": [
                    "금융 디지털화 트렌드와 자신의 역량 연결 (핀테크·빅데이터·AI 금융 등)",
                    "신한 SOL, 신한카드 등 계열사 서비스 사용 경험 기반 개선 아이디어",
                    "고객 중심 사고와 실제 문제 해결 경험 구체화",
                    "은행권 자격증 (은행FP, 투자자산운용사 등) 보유 시 적극 어필",
                ],
                "interview_points": [
                    "NCS 직업기초능력평가 및 금융 직무 지식 테스트 대비 필수",
                    "최근 금융 이슈(금리 변화, 인터넷은행 경쟁 등) 사전 파악",
                    "디지털 금융 트렌드(CBDC, 오픈뱅킹, 마이데이터) 기본 개념 정리",
                    "PT 면접: 금융 관련 사회 현안 분석 및 은행의 대응 방향 논리적 제시",
                ],
            },
        ]

        for pd_item in prep_data:
            company_name = pd_item.pop("company_name")
            company_obj = next((c for c in company_objects if c.name == company_name), None)
            if company_obj:
                snap = PrepSnapshot(
                    company_id=company_obj.id,
                    generated_at=now,
                    created_at=now,
                    **pd_item,
                )
                db.add(snap)

        db.flush()
        print(f"  ✅ PrepSnapshot {len(prep_data)}개 생성 완료")

        # ── 4. 오늘 브리핑 (user_id=1) ────────────────────
        print("📰 오늘 브리핑 생성 중...")
        today = date.today()

        samsung = next(c for c in company_objects if c.name == "삼성전자")
        hyundai = next(c for c in company_objects if c.name == "현대자동차")
        kakao = next(c for c in company_objects if c.name == "카카오")

        briefing = Briefing(
            user_id=1,
            briefing_date=today,
            title=f"{today.strftime('%Y년 %m월 %d일')} 관심기업 브리핑",
            created_at=now,
        )
        db.add(briefing)
        db.flush()

        items = [
            BriefingItem(
                briefing_id=briefing.id,
                company_id=samsung.id,
                source_type="news",
                headline="삼성전자, HBM4 4분기 양산 공식 확인",
                summary="삼성전자가 2024년 4분기 내 HBM4 양산을 시작한다고 공식 발표. 엔비디아 차세대 블랙웰 GPU 탑재 유력.",
                action_point="반도체 직군 지원자라면 HBM 구조와 삼성 DS부문 전략 숙지 필수.",
                sort_order=1,
                created_at=now,
            ),
            BriefingItem(
                briefing_id=briefing.id,
                company_id=samsung.id,
                source_type="job",
                headline="[마감 D-14] 삼성전자 2024 상반기 DS부문 신입사원 공채",
                summary="반도체 설계·공정 직군 중심. 학사 이상, GSAT 필기 전형 포함. 지원 마감: 2024-02-29.",
                action_point="GSAT 준비 병행 필수. 직무 기술서 꼼꼼히 읽고 경험과 매칭하여 자소서 작성 권장.",
                sort_order=2,
                created_at=now,
            ),
            BriefingItem(
                briefing_id=briefing.id,
                company_id=hyundai.id,
                source_type="news",
                headline="현대차, 미국 조지아 전기차 공장 가동 개시",
                summary="현대차 메타플랜트 아메리카(HMGMA)가 아이오닉5 생산을 시작. 연간 30만대 생산 목표.",
                action_point="전동화·해외 생산 전략 관련 면접 질문 대비. 아이오닉 라인업 숙지 권장.",
                sort_order=3,
                created_at=now,
            ),
            BriefingItem(
                briefing_id=briefing.id,
                company_id=hyundai.id,
                source_type="job",
                headline="현대자동차 2024 상반기 연구개발 직군 공채",
                summary="전동화·SDV·로보틱스 R&D 직군 채용. 기계·전기전자·컴퓨터 전공 우대. HMAT 전형 포함.",
                action_point="SDV(소프트웨어 정의 자동차) 관련 프로젝트 경험 자소서에 강조. 포트폴리오 준비 권장.",
                sort_order=4,
                created_at=now,
            ),
            BriefingItem(
                briefing_id=briefing.id,
                company_id=kakao.id,
                source_type="news",
                headline="카카오, AI 어시스턴트 '카나나' 베타 서비스 시작",
                summary="카카오가 자체 개발 LLM 기반 AI 서비스 카나나 베타를 출시. 카카오톡 연동 개인화 서비스 제공.",
                action_point="카카오 AI 전략과 서비스 사용 경험을 면접 시 적극 활용 권장.",
                sort_order=5,
                created_at=now,
            ),
            BriefingItem(
                briefing_id=briefing.id,
                company_id=kakao.id,
                source_type="news",
                headline="카카오페이, 해외 결제 서비스 동남아 3개국 확장",
                summary="카카오페이가 태국·베트남·인도네시아에서 QR 결제 서비스를 개시. 글로벌 핀테크 시장 공략 가속화.",
                action_point="카카오 핀테크 사업 확장 전략 숙지. 글로벌 관심 어필 기회 활용.",
                sort_order=6,
                created_at=now,
            ),
        ]

        for item in items:
            db.add(item)
        db.flush()
        print(f"  ✅ BriefingItem {len(items)}개 생성 완료")

        # ── 5. 구독 (user_id=1, 삼성전자·현대차·카카오) ──────
        print("⭐ 관심기업 구독 생성 중...")
        for company_obj in [samsung, hyundai, kakao]:
            sub = Subscription(user_id=1, company_id=company_obj.id)
            db.add(sub)

        db.commit()
        print("\n✅ 시드 데이터 삽입 완료!")
        print("  - 유저: 1명 (id=1, dev@jobpilot.kr)")
        print(f"  - 기업: {len(company_objects)}개")
        print(f"  - PrepSnapshot: {len(prep_data)}개")
        print("  - 브리핑: 오늘 1건 (6개 아이템)")
        print("  - 구독: 3개 (삼성전자, 현대자동차, 카카오)")

    except Exception as e:
        db.rollback()
        print(f"❌ 시드 실패: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
