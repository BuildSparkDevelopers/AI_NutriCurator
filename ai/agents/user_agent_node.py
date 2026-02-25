from __future__ import annotations

from enum import Enum
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
    def _normalize_raw(value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        return value

    @staticmethod
    def _as_flag(value: Any) -> int:
        value = ProfileRetrieval._normalize_raw(value)
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, float)):
            return int(value > 0)
        if isinstance(value, list):
            if not value:
                return 0
            normalized = []
            for item in value:
                raw = ProfileRetrieval._normalize_raw(item)
                normalized.append(str(raw).strip().lower())
            meaningful = [txt for txt in normalized if txt not in {"", "n/a", "na", "none", "null", "0"}]
            return int(bool(meaningful))
        if value is None:
            return 0
        txt = str(value).strip().lower()
        if "." in txt:
            txt = txt.rsplit(".", 1)[-1]
        return 0 if txt in {"", "n/a", "na", "none", "null", "0"} else 1

    @staticmethod
    def _allergy_list(raw_allergy: Any) -> List[str]:
        if isinstance(raw_allergy, list):
            normalized = []
            for v in raw_allergy:
                raw = v.value if isinstance(v, Enum) else v
                txt = str(raw).strip()
                if txt and txt.lower() not in {"n/a", "na", "none", "null", ""}:
                    normalized.append(txt)
            return normalized
        if not raw_allergy:
            return []
        if isinstance(raw_allergy, Enum):
            raw_allergy = raw_allergy.value
        txt = str(raw_allergy).strip()
        if txt.lower() in {"n/a", "na", "none", "null", ""}:
            return []
        return [part.strip() for part in txt.split(",") if part.strip()]

    def run(self, state: Dict[str, Any], config: Any = None) -> Dict[str, Any]:
        user_id = str(state.get("user_id", "0"))
        profile = self._fetch_profile(state)

        raw_diabetes = self._normalize_raw(profile.get("diabetes_flag", profile.get("diabetes")))
        raw_hypertension = self._normalize_raw(profile.get("hypertension_flag", profile.get("hypertension")))
        raw_kidneydisease = self._normalize_raw(profile.get("kidneydisease_flag", profile.get("kidneydisease")))

        diabetes_flag = self._as_flag(raw_diabetes)
        hypertension_flag = self._as_flag(raw_hypertension)
        kidneydisease_flag = self._as_flag(raw_kidneydisease)

        raw_allergy = profile.get("allergy_detail", profile.get("allergy_list", profile.get("allergy")))
        allergy_detail = self._allergy_list(raw_allergy)
        allergy_flag = 1 if allergy_detail else 0

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

        if allergy_detail:
            final_profile["restricted_ingredients"] = list(
                set(final_profile.get("restricted_ingredients", []) + allergy_detail)
            )

        normalized_profile = {
            **profile,
            "diabetes_flag": diabetes_flag,
            "hypertension_flag": hypertension_flag,
            "kidneydisease_flag": kidneydisease_flag,
            "allergy_flag": allergy_flag,
            "allergy_detail": allergy_detail,
            "allergy_list": allergy_detail,
            "weight": weight,
        }

        return {
            "diabetes_flag": diabetes_flag,
            "hypertension_flag": hypertension_flag,
            "kidneydisease_flag": kidneydisease_flag,
            "allergy_flag": allergy_flag,
            "diabetes_detail": raw_diabetes if diabetes_flag == 1 else None,
            "hypertension_detail": raw_hypertension if hypertension_flag == 1 else None,
            "kidney_detail": raw_kidneydisease if kidneydisease_flag == 1 else None,
            "allergy_detail": allergy_detail,
            "allergy_list": allergy_detail,
            "final_profile": final_profile,
            "user_profile": normalized_profile,
            "next_step": "orch_agent",
        }
