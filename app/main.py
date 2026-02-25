 # 역할: FastAPI 앱 생성 + 라우터 연결(서버 시작점)

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.products import router as products_router
from api.routes.ai import router as ai_router
from api.routes.cart import router as cart_router

app = FastAPI(title="AI-NutriCurator API")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(ai_router)    
app.include_router(cart_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



