# 환경변수(.env)에서 JWT 설정을 읽어서 settings로 제공

from pydantic_settings import BaseSettings, SettingsConfigDict

import os

class Settings:
    # JWT 설정 (로컬 테스트 기본값)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRES_MINUTES: int = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

    # username 정책
    USERNAME_MIN_LEN: int = 4
    USERNAME_MAX_LEN: int = 20

    # password 정책
    PASSWORD_MIN_LEN: int = 10
    PASSWORD_MAX_LEN: int = 72



class Settings(BaseSettings):
    # DB 접속 URL
    DATABASE_URL: str

    #SettingsConfigDict: Settings가 환경변수를 어떻게 읽을지 설정하는 옵션들
    model_config = SettingsConfigDict(
        env_file=".env",                # 로컬 개발 시 프로젝트 루트의 .env 파일에서 환경변수를 읽음
        env_file_encoding="utf-8",      # .env 파일 인코딩 지정 (윈도우/특수문자 환경에서 안전하게 읽기 위함)
        extra="ignore",                # .env에 POSTGRES_USER 같은 "정의되지 않은 키"가 있어도 무시 (에러 방지) 
    )



settings = Settings()
