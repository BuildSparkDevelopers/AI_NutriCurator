from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # =========================
    # JWT
    # =========================
    JWT_SECRET_KEY: str = "dev-secret-change-me"   # 로컬 기본값
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # =========================
    # Auth 정책
    # =========================
    USERNAME_MIN_LEN: int = 3
    USERNAME_MAX_LEN: int = 20

    PASSWORD_MIN_LEN: int = 8
    # bcrypt는 72 넘어가면 잘리거나 문제될 수 있어서 72 추천
    PASSWORD_MAX_LEN: int = 72

    # =========================
    # Postgres (.env에서 읽음)
    # =========================
    POSTGRES_DB: str = "appdb"
    POSTGRES_USER: str = "appuser"
    POSTGRES_PASSWORD: str = "apppassword"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    AI_DATA_SOURCE: str = "postgres"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()