from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, Dict

from api.deps import get_current_user_id

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

class AnalyzeReq(BaseModel):
    product_id: int

@router.post("/analyze")
def analyze(req: AnalyzeReq, user_id: int = Depends(get_current_user_id)) -> Dict[str, Any]:
    #  TODO: orche 연결 전까지 임시 응답
    # TODO: connect orchestrator when run() entrypoint is ready
    return {"status": "ok", "msg": "endpoint wired", "alternatives": []}
