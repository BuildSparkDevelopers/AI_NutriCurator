import math
from typing import Dict, Any, List, Set, Optional, TypedDict


# =========================
# ✅ sub에게 넘길 스키마
# =========================
class Candidate(TypedDict):
    product_id: int
    rank: int  # 1..K

class RecoToSubPayload(TypedDict):
    candidates: List[Candidate]


# =========================
# ✅ Reco Engine (OOP)
# =========================
class RecoEngine:
    def __init__(
        self,
        fake_db: Dict[str, Any],
        taste_lexicon: Dict[str, List[str]],
        type_lexicon: Dict[str, List[str]],
        snack_categories: List[str],
        category_neighbors: Dict[str, List[str]],
        generic_taste_stop: Optional[Set[str]] = None,
    ):
        self.fake_db = fake_db
        self.taste_lexicon = taste_lexicon
        self.type_lexicon = type_lexicon
        self.snack_categories = snack_categories

        self.category_neighbors = self.make_neighbors_symmetric(category_neighbors)
        self.generic_taste_stop = generic_taste_stop or {
            "butter", "corn", "potato", "salty", "milk", "sugar", "wheat", "soy",
            "sesame", "seaweed"
        }

        # 최종 인덱스 DB
        self.final_db: Dict[int, Dict[str, Any]] = {}

    # -------------------------
    # Utils (원래 로직 그대로)
    # -------------------------
    @staticmethod
    def norm_cat(x: Any) -> str:
        return (x or "").strip().lower()

    def extract_taste_tags(self, text: str) -> List[str]:
        text_l = (text or "").lower()
        tags = []
        for tag, kws in self.taste_lexicon.items():
            for kw in kws:
                if kw.lower() in text_l:
                    tags.append(tag)
                    break
        return sorted(set(tags))

    def extract_lexicon_tags(self, text: str, lexicon: Dict[str, List[str]]) -> List[str]:
        # (현재 코드에서는 TYPE_LEXICON 등 다른 용도로 쓸 수 있어서 유지)
        text_l = (text or "").lower()
        tags: List[str] = []
        for tag, kws in lexicon.items():
            for kw in kws:
                if kw.lower() in text_l:
                    tags.append(tag)
                    break
        return sorted(set(tags))

    @staticmethod
    def token_overlap_score(a_text: str, b_text: str) -> int:
        a = set((a_text or "").lower().split())
        b = set((b_text or "").lower().split())
        return len(a & b)

    @staticmethod
    def make_neighbors_symmetric(neighbors: Dict[str, List[str]]) -> Dict[str, List[str]]:
        out = {k: list(v) for k, v in neighbors.items()}
        for a, bs in neighbors.items():
            for b in bs:
                out.setdefault(b, [])
                if a not in out[b]:
                    out[b].append(a)
        return out

    @staticmethod
    def _alloc_counts(k: int, weights: List[float]) -> List[int]:
        """k를 weights 비율로 정수 개수로 배분(합이 k가 되도록)"""
        raw = [k * w for w in weights]
        base = [int(math.floor(x)) for x in raw]
        remain = k - sum(base)

        frac = [(raw[i] - base[i], i) for i in range(len(weights))]
        frac.sort(reverse=True)
        for _, i in frac[:remain]:
            base[i] += 1
        return base

    def build_index_text(self, p: Dict[str, Any]) -> str:
        name = p.get("name", "")
        brand = p.get("brand", "")
        ingredients_list = p.get("ingredients", [])
        ing = " ".join(ingredients_list)
        cat = p.get("category", "")

        # 1) 기본 텍스트 구성
        base_text = f"{name} {brand} {ing}"

        # 2) 조건부 맛 태그 추출 (카테고리 제한) - 기존 로직 유지
        taste_tags: List[str] = []
        if any(snack_cat in cat for snack_cat in self.snack_categories):
            taste_tags = self.extract_taste_tags(base_text)

        # 3) 텍스트 조립
        taste_text = " ".join([f"taste:{t}" for t in taste_tags]) if taste_tags else ""
        cat_text = f"category:{cat}" if cat else "category:unknown"

        return " ".join([
            f"name:{name}",
            f"brand:{brand}",
            f"ingredients:{ing}",
            taste_text,
            cat_text,
        ]).strip()

    def get_taste_tag_set(self, p: Dict[str, Any]) -> Set[str]:
        toks = (p.get("index_text") or "").lower().split()
        return {t.split("taste:", 1)[1] for t in toks if t.startswith("taste:")}

    def filtered_taste_set(self, p: Dict[str, Any]) -> Set[str]:
        tastes = self.get_taste_tag_set(p)
        return {t for t in tastes if t not in self.generic_taste_stop}

    # -------------------------
    # Build final_db
    # -------------------------
    def build_final_db(self) -> Dict[int, Dict[str, Any]]:
        self.final_db = {}
        products = self.fake_db.get("products", {})

        for pid, p in products.items():
            pid_int = int(pid)
            index_text = self.build_index_text(p)

            self.final_db[pid_int] = {
                **p,  # 원본 유지
                "product_id": pid_int,
                "index_text": index_text,
                # ✅ allergen_tags 제거됨
            }

        return self.final_db

    # -------------------------
    # Retrieval (로직 그대로)
    # -------------------------
    def retrieve_candidates_v1_light_unified_k(
        self,
        clicked_product_id: int,
        k: int = 3,
        weights: List[float] = [0.6, 0.3, 0.1],  # bucket1, bucket2, bucket3
    ) -> List[Dict[str, Any]]:

        clicked = self.final_db.get(clicked_product_id)
        if not clicked:
            return []

        clicked_cat = self.norm_cat(clicked.get("category"))
        clicked_tastes = self.get_taste_tag_set(clicked)
        clicked_text = clicked.get("index_text") or ""
        neighbor_set = {self.norm_cat(c) for c in self.category_neighbors.get(clicked_cat, [])}

        bucket1, bucket2, bucket3, bucket4 = [], [], [], []

        for pid, p in self.final_db.items():
            if pid == clicked_product_id:
                continue

            cat = self.norm_cat(p.get("category"))
            tastes = self.get_taste_tag_set(p)

            taste_overlap = len(clicked_tastes & tastes)
            fallback = self.token_overlap_score(clicked_text, p.get("index_text") or "")

            row = {
                "product_id": pid,
                "name": p.get("name"),
                "category": cat,
                "tastes": sorted(tastes),
                "taste_score": taste_overlap,
                "fallback_score": fallback,
                "final_score": (taste_overlap * 10) + fallback,
            }

            if cat == clicked_cat:
                (bucket1 if taste_overlap > 0 else bucket2).append(row)
            elif cat in neighbor_set:
                (bucket3 if taste_overlap > 0 else bucket4).append(row)
            else:
                bucket4.append(row)

        def sort_key(r):
            return (r["taste_score"], r["fallback_score"], -r["product_id"])

        for b in (bucket1, bucket2, bucket3, bucket4):
            b.sort(key=sort_key, reverse=True)

        # ✅ k로부터 자동으로 n1,n2,n3 계산 (기존 로직)
        n1, n2, n3 = self._alloc_counts(k, weights)

        picked = bucket1[:n1] + bucket2[:n2] + bucket3[:n3]

        # 부족하면 bucket4로 채워서 딱 k 맞춤
        if len(picked) < k:
            picked += bucket4[: (k - len(picked))]

        return picked[:k]

    # -------------------------
    # ✅ sub에게 넘길 payload + debug 생성
    # -------------------------
    def run(
        self,
        clicked_product_id: int,
        k: int = 5,
        weights: List[float] = [0.6, 0.3, 0.1],
    ) -> tuple[RecoToSubPayload, Dict[str, Any]]:

        if not self.final_db:
            self.build_final_db()

        clicked = self.final_db.get(clicked_product_id)
        res = self.retrieve_candidates_v1_light_unified_k(
            clicked_product_id=clicked_product_id,
            k=k,
            weights=weights
        )

        # ✅ sub용 payload (스키마 고정)
        reco_to_sub: RecoToSubPayload = {
            "candidates": [
                {"product_id": r["product_id"], "rank": i + 1}
                for i, r in enumerate(res)
            ]
        }

        # ✅ 디버그(원하는 만큼 넣어도 sub에는 안 보냄)
        reco_debug: Dict[str, Any] = {
            "clicked": {
                "product_id": clicked_product_id,
                "name": clicked.get("name") if clicked else None,
                "category": self.norm_cat(clicked.get("category")) if clicked else None,
                "tastes": sorted(self.get_taste_tag_set(clicked)) if clicked else [],
            },
            "k": k,
            "weights": weights,
            "candidates_detail": res,  # taste_score/fallback_score/final_score 포함
        }

        return reco_to_sub, reco_debug


# =========================
# ✅ 사용 예시
# =========================
engine = RecoEngine(
    fake_db=FAKE_DB,
    taste_lexicon=TASTE_LEXICON,
    type_lexicon=TYPE_LEXICON,
    snack_categories=SNACK_CATEGORIES,
    category_neighbors=CATEGORY_NEIGHBORS,
)

reco_to_sub, reco_debug = engine.run(clicked_product_id=10, k=5)
print(reco_to_sub)


from typing import TypedDict, Any, Dict, Optional, List

# -------------------------
# sub에게 넘길 payload 스키마(너가 쓰는 그대로)
# -------------------------
class Candidate(TypedDict):
    product_id: int
    rank: int

class RecoToSubPayload(TypedDict):
    candidates: List[Candidate]

# -------------------------
# LangGraph 스타일의 "State"
# -------------------------
class RecoState(TypedDict, total=False):
    # input
    clicked_product_id: int
    k: int
    weights: List[float]

    # output
    reco_to_sub: RecoToSubPayload
    reco_debug: Dict[str, Any]

    # error
    error: Optional[str]


# -------------------------
# ✅ 진짜 "노드": state -> state
# -------------------------
def reco_node(state: RecoState, engine: "RecoEngine") -> RecoState:
    try:
        clicked_product_id = state["clicked_product_id"]
        k = state.get("k", 5)
        weights = state.get("weights", [0.6, 0.3, 0.1])

        reco_to_sub, reco_debug = engine.run(
            clicked_product_id=clicked_product_id,
            k=k,
            weights=weights
        )

        state["reco_to_sub"] = reco_to_sub
        state["reco_debug"] = reco_debug
        state["error"] = None
        return state

    except Exception as e:
        state["error"] = f"[reco_node] {type(e).__name__}: {e}"
        return state


# ✅ 엔진 생성 (너 코드 그대로)
engine = RecoEngine(
    fake_db=FAKE_DB,
    taste_lexicon=TASTE_LEXICON,
    type_lexicon=TYPE_LEXICON,
    snack_categories=SNACK_CATEGORIES,
    category_neighbors=CATEGORY_NEIGHBORS,
)

# ✅ "그래프 state" 처럼 입력 준비
state: RecoState = {
    "clicked_product_id": 10,
    "k": 5,
    "weights": [0.6, 0.3, 0.1],
}

# ✅ 노드 실행
state = reco_node(state, engine)

# ✅ 에러 체크
if state.get("error"):
    print("ERROR:", state["error"])
else:
    print("=== reco_to_sub (sub에게 전달) ===")
    print(state["reco_to_sub"])

    print("\n=== reco_debug (개발자 확인용) ===")
    for r in state["reco_debug"]["candidates_detail"]:
        print(f"- {r['product_id']} {r['name']}"
              f" | taste_score={r['taste_score']}"
              f" | fallback_score={r['fallback_score']}"
              f" | final_score={r['final_score']:.2f}"
              f" | tastes={r['tastes']}")
