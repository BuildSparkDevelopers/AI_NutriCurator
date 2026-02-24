from __future__ import annotations

from typing import Any, Dict, List

from domain.rules.nutrient_rules import generate_final_profile


class ProfileRetrieval:
    def __init__(self, model: Any | None = None):
        self.llm = model

    def _fetch_profile(self, state: Dict[str, Any]) -> Dict[str, Any]:
        existing = state.get("user_profile")
        if isinstance(existing, dict) and existing:
            return existing
        return {
            "diabetes": "N/A",
            "hypertension": "N/A",
            "kidneydisease": "N/A",
            "allergy": "N/A",
            "weight": 70.0,
        }

    @staticmethod
    def _as_flag(value: Any) -> int:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value > 0)
        if value is None:
            return 0
        txt = str(value).strip().lower()
        return 0 if txt in {"", "n/a", "na", "none", "null", "0"} else 1

    @staticmethod
    def _allergy_list(raw_allergy: Any) -> List[str]:
        if isinstance(raw_allergy, list):
            return [str(v).strip() for v in raw_allergy if str(v).strip()]
        if not raw_allergy:
            return []
        txt = str(raw_allergy).strip()
        if txt.lower() in {"n/a", "na", "none", "null", ""}:
            return []
        return [part.strip() for part in txt.split(",") if part.strip()]

    def run(self, state: Dict[str, Any], config: Any = None) -> Dict[str, Any]:
        user_id = str(state.get("user_id", "0"))
        profile = self._fetch_profile(state)

        diabetes_flag = self._as_flag(profile.get("diabetes_flag", profile.get("diabetes")))
        hypertension_flag = self._as_flag(profile.get("hypertension_flag", profile.get("hypertension")))
        kidneydisease_flag = self._as_flag(profile.get("kidneydisease_flag", profile.get("kidneydisease")))
        allergy_flag = self._as_flag(profile.get("allergy_flag", profile.get("allergy")))

        try:
            weight = float(profile.get("weight", 70.0))
        except (TypeError, ValueError):
            weight = 70.0

        final_profile = generate_final_profile(
            user_id=user_id,
            user_diseases={
                "allergy": allergy_flag,
                "kidneydisease": kidneydisease_flag,
                "diabetes": diabetes_flag,
                "hypertension": hypertension_flag,
            },
            user_weight=weight,
        )

        allergy_list = self._allergy_list(profile.get("allergy_list", profile.get("allergy")))
        if allergy_list:
            final_profile["restricted_ingredients"] = list(
                set(final_profile.get("restricted_ingredients", []) + allergy_list)
            )

        normalized_profile = {
            **profile,
            "diabetes_flag": diabetes_flag,
            "hypertension_flag": hypertension_flag,
            "kidneydisease_flag": kidneydisease_flag,
            "allergy_flag": allergy_flag,
            "allergy_list": allergy_list,
            "weight": weight,
        }

        return {
            "diabetes_flag": diabetes_flag,
            "hypertension_flag": hypertension_flag,
            "kidneydisease_flag": kidneydisease_flag,
            "allergy_flag": allergy_flag,
            "diabetes_detail": normalized_profile.get("diabetes"),
            "hypertension_detail": normalized_profile.get("hypertension"),
            "kidney_detail": normalized_profile.get("kidneydisease"),
            "allergy_list": allergy_list,
            "final_profile": final_profile,
            "user_profile": normalized_profile,
            "next_step": "orch_agent",
        }
