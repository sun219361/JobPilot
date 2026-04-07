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
    subscription_limit: int = 5  # 관심기업 최대 등록 수 (환경변수로 오버라이드)


settings = Settings()
