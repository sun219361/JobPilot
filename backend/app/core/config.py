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


settings = Settings()
