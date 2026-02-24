from __future__ import annotations

from typing import Any, Dict, Optional


class FakeHealthProfileRepository:
    def __init__(self, users: Dict[Any, Dict[str, Any]]):
        self.users = users

    def get_by_user_id(self, user_id: int) -> Optional[dict]:
        row = self.users.get(user_id)
        if row is None:
            return {
                "diabetes": "N/A",
                "hypertension": "N/A",
                "kidneydisease": "N/A",
                "allergy": "N/A",
                "weight": 70.0,
            }
        return {
            "diabetes": row.get("diabetes", "N/A"),
            "hypertension": row.get("hypertension", "N/A"),
            "kidneydisease": row.get("kidneydisease", "N/A"),
            "allergy": row.get("allergy", "N/A"),
            "weight": row.get("weight", 70.0),
        }
