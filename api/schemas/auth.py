 # 역할: auth 요청/응답 스키마(문서 자동화 + 검증)

from pydantic import BaseModel, Field

class SignupRequest(BaseModel):
    username: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=72)

    is_tos_agreed: bool
    is_privacy_agreed: bool
    is_sensitive_agreed: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):  
    access_token: str
    token_type: str = "bearer"
