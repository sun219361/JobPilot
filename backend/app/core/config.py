from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # Database
    database_url: str = "postgresql+psycopg2://jobpilot:jobpilot@localhost:5432/jobpilot"
    database_url_async: str = "postgresql+asyncpg://jobpilot:jobpilot@localhost:5432/jobpilot"

    # Business Rules
    subscription_limit: int = 5

    # News Collection
    news_provider: str = "naver"          # 사용할 뉴스 provider
    naver_client_id: str = ""             # 네이버 오픈API 클라이언트 ID
    naver_client_secret: str = ""         # 네이버 오픈API 클라이언트 시크릿
    news_default_limit: int = 5           # 기업당 기본 수집 개수
    news_lookback_days: int = 3           # 최근 며칠치 기준

    # Briefing Generation
    briefing_news_lookback_days: int = 3       # 브리핑에 포함할 뉴스 기준 최근 며칠
    briefing_max_items_per_company: int = 2    # 기업당 최대 브리핑 아이템 수
    briefing_max_companies_per_user: int = 5   # 사용자당 최대 반영 기업 수

    # Job Posting Collection (Phase 3)
    job_provider: str = "saramin"              # 사용할 채용공고 provider
    saramin_api_key: str = ""                  # 사람인 오픈API 인증키
    job_default_limit: int = 5                 # 기업당 기본 수집 개수
    job_lookback_days: int = 30                # 최근 며칠치 기준
    job_keywords: str = "Python,SQL,데이터,AI,금융,협업"  # rule-based 키워드 목록 (쉼표 구분)

    # Prep Snapshot Generation (Phase 4)
    # 생성 대상 정책: "subscriptions" (관심기업만) | "all" (전체 기업)
    prep_target_mode: str = "subscriptions"
    # 뉴스 조회 기준 일수 (최근 N일 이내)
    prep_news_lookback_days: int = 7
    # snapshot 생성 시 사용할 최대 뉴스 건수
    prep_max_news_items: int = 3
    # snapshot 생성 시 사용할 최대 채용공고 건수
    prep_max_job_items: int = 3
    # 생성 정책: "daily" (하루 1개) | "always" (매번 새로 생성)
    prep_generation_mode: str = "daily"

    # ── JWT Authentication (Phase 5) ──────────────────────────────────────
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_STRONG_RANDOM_KEY"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


settings = Settings()
