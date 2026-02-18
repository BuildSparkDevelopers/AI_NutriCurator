# 환경변수(.env)에서 JWT 설정을 읽어서 settings로 제공


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

settings = Settings()
