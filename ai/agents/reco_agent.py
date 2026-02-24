from __future__ import annotations

from typing import Any, Dict, List


class Recommendation:
    """
    Minimal recommendation node for LangGraph.
    Produces `state["candidates"]` for sub-reco agent.
    """

    def __init__(self, products_db: Dict[str, Dict[str, Any]] | None = None):
        self.products_db = products_db or {}

    @staticmethod
    def _to_int(value: Any, default: int = 0) -> int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _collect_candidates(self, clicked_id: int, k: int) -> List[Dict[str, int]]:
        candidates: List[Dict[str, int]] = []

        for _, product in self.products_db.items():
            pid = self._to_int(product.get("product_id"))
            if pid <= 0 or pid == clicked_id:
                continue
            candidates.append({"product_id": pid, "rank": 0})

        candidates.sort(key=lambda row: row["product_id"])
        picked = candidates[: max(1, k)]
        for idx, row in enumerate(picked, start=1):
            row["rank"] = idx
        return picked

    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        clicked_product_id = self._to_int(state.get("product_id"))
        k = self._to_int(state.get("k", 5), default=5)

        candidates = self._collect_candidates(clicked_product_id, k)
        return {
            "candidates": candidates,
            "next_step": "sub_reco_agent",
        }
