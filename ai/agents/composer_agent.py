from __future__ import annotations

from typing import Any, Dict, List


class ResponseGeneration:
    """Final response composer node."""

    @staticmethod
    def _top_recommendations(sub_recommendations: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        sorted_rows = sorted(sub_recommendations, key=lambda row: row.get("score", 0), reverse=True)
        return sorted_rows[:limit]

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        any_exceed = bool(state.get("any_exceed", False))
        any_allergen = bool(state.get("any_allergen", False))
        sub_recommendations = state.get("sub_recommendations", [])

        if any_exceed or any_allergen:
            top_rows = self._top_recommendations(sub_recommendations, limit=3)
            if top_rows:
                reason = "주의 성분이 감지되어 대체 상품을 추천합니다."
            else:
                reason = "주의 성분이 감지되었지만 대체 상품을 찾지 못했습니다."
        else:
            reason = "현재 상품은 프로필 기준에서 비교적 안전합니다."

        return {
            "final_answer": reason,
            "sub_recommendations": sub_recommendations,
            "next_step": "end",
        }
