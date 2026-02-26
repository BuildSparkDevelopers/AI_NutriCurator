import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_PRODUCTS_CSV = BASE_DIR / "infra" / "db" / "products (1).csv"
TARGET_PRODUCTS_CSV = BASE_DIR / "infra" / "db" / "products.csv"
CATEGORIES_CSV = BASE_DIR / "infra" / "db" / "categories.csv"
REPORT_CSV = BASE_DIR / "infra" / "db" / "category_mapping_report.csv"


def normalize(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = s.replace("·", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", "", s)
    for w in ("식품", "가공품", "가공", "제품", "류"):
        s = s.replace(w, "")
    return s


def token_set(text: str) -> set[str]:
    s = (text or "").strip().lower().replace("·", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    toks = {t for t in re.split(r"\s+", s) if t}
    cleaned = set()
    for t in toks:
        for w in ("식품", "가공품", "가공", "제품", "류"):
            t = t.replace(w, "")
        if t:
            cleaned.add(t)
    return cleaned


def match_score(src: str, dst: str) -> float:
    a = normalize(src)
    b = normalize(dst)
    if not a or not b:
        return 0.0
    ratio = SequenceMatcher(None, a, b).ratio()
    sa = token_set(src)
    sb = token_set(dst)
    jaccard = (len(sa & sb) / len(sa | sb)) if (sa or sb) else 0.0
    contains_bonus = 0.08 if (a in b or b in a) else 0.0
    return ratio * 0.7 + jaccard * 0.3 + contains_bonus


def has_kw(text: str, kws: list[str]) -> bool:
    n = normalize(text)
    return any(k in n for k in kws)


def load_categories() -> list[dict]:
    out = []
    with CATEGORIES_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            cid = (row.get("category_id") or "").strip()
            name = (row.get("name") or "").strip()
            if cid and name:
                out.append({"category_id": cid, "name": name})
    return out


def rule_based_mapping(raw_category: str) -> str | None:
    raw = raw_category or ""

    # 1) 특정 타겟층 대상 식품 -> 기타식품류
    target_kws = [
        "영아", "유아", "어린이", "아동", "임산부", "수유부",
        "노인", "고령", "환자", "선천성대사질환", "특수의료",
        "체중조절", "조제식", "특수영양",
    ]
    if has_kw(raw, target_kws):
        return "기타식품류"

    # 2) 원료 오리진 유사 기준
    if has_kw(raw, ["소", "쇠고기", "돼지", "닭", "육", "햄", "소시지", "포장육", "순대"]):
        return "식육가공품 및 포장육"
    if has_kw(raw, ["어묵", "어육", "수산", "생선", "참치", "오징어", "새우", "게", "해산", "해물"]):
        return "수산가공식품류"
    if has_kw(raw, ["계란", "난백", "난황", "전란", "알가공", "난가공"]):
        return "알가공품류"
    if has_kw(raw, ["우유", "요구르트", "요거트", "치즈", "버터", "유가공"]):
        return "유가공품류"
    if has_kw(raw, ["아이스크림", "아이스밀크", "샤베트", "빙과"]):
        return "빙과류"
    if has_kw(raw, ["꿀", "벌꿀", "화분", "프로폴리스"]):
        return "벌꿀 및 화분가공품류"
    if has_kw(raw, ["곡물", "밀가루", "쌀", "보리", "고구마", "감자", "채소", "과일", "버섯", "농산"]):
        return "농산가공식품류"

    # 3) 가공방식 유사 기준
    if has_kw(raw, ["절임", "장아찌", "피클", "조림", "정과"]):
        return "절임류 또는 조림류"
    if has_kw(raw, ["된장", "고추장", "간장", "청국장", "장류"]):
        return "장류"
    if has_kw(raw, ["소스", "드레싱", "케첩", "마요네즈", "카레", "향신료", "조미"]):
        return "조미식품"
    if has_kw(raw, ["면", "라면", "우동", "국수", "파스타", "당면"]):
        return "면류"
    if has_kw(raw, ["빵", "과자", "쿠키", "크래커", "떡", "시리얼"]):
        return "과자류·빵류 또는 떡류"
    if has_kw(raw, ["캔디", "사탕", "껌", "양갱", "캐러멜", "당류"]):
        return "당류"
    if has_kw(raw, ["초콜릿", "코코아"]):
        return "코코아가공품류 또는 초콜릿류"
    if has_kw(raw, ["잼", "마멀레이드"]):
        return "잼류"
    if has_kw(raw, ["두부", "묵"]):
        return "두부류 또는 묵류"
    if has_kw(raw, ["기름", "유지", "쇼트닝", "마가린"]):
        return "식용유지류"
    if has_kw(raw, ["커피", "차", "음료", "주스", "드링크", "탄산", "액상차", "고형차"]):
        return "음료류"
    if has_kw(raw, ["와인", "맥주", "소주", "리큐르", "주류"]):
        return "주류"
    if has_kw(raw, ["즉석", "레토르트", "간편", "냉동식품", "밀키트", "hmr"]):
        return "즉석식품류"

    return None


def best_similarity_mapping(raw_category: str, categories: list[dict]) -> tuple[str, str, float]:
    best_name = ""
    best_id = ""
    best_score = -1.0
    for c in categories:
        s = match_score(raw_category, c["name"])
        if s > best_score:
            best_score = s
            best_name = c["name"]
            best_id = c["category_id"]
    return best_name, best_id, round(max(best_score, 0.0), 4)


def main() -> None:
    categories = load_categories()
    category_id_by_name = {c["name"]: c["category_id"] for c in categories}

    with SOURCE_PRODUCTS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise RuntimeError("Source products file is empty.")

    header = rows[0]
    data = rows[1:]

    if "카테고리" in header:
        category_idx = header.index("카테고리")
    else:
        category_idx = next((i for i, h in enumerate(header) if "category" in h.lower()), -1)
        if category_idx < 0:
            raise RuntimeError("Could not find category column in source products.")

    new_header = header + ["mapped_category", "category_id", "score"]
    out_rows = [new_header]

    cache: dict[str, tuple[str, str, float]] = {}

    for row in data:
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        raw_cat = row[category_idx].strip()

        if raw_cat not in cache:
            mapped_name, mapped_id, score = best_similarity_mapping(raw_cat, categories)

            # score < 0.5 대상은 사용자 지정 3개 규칙으로 재매핑
            if score < 0.5:
                rule_name = rule_based_mapping(raw_cat)
                if rule_name:
                    mapped_name = rule_name
                    mapped_id = category_id_by_name.get(rule_name, "pf24")
                    score = max(score, 0.5)

            cache[raw_cat] = (mapped_name, mapped_id, round(score, 4))

        mapped_name, mapped_id, score = cache[raw_cat]
        out_rows.append(row + [mapped_name, mapped_id, f"{score:.4f}"])

    with TARGET_PRODUCTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(out_rows)

    report_rows = []
    for raw_cat, (mapped_name, mapped_id, score) in cache.items():
        report_rows.append(
            {
                "raw_category": raw_cat,
                "mapped_category": mapped_name,
                "mapped_category_id": mapped_id,
                "score": f"{score:.4f}",
            }
        )
    report_rows.sort(key=lambda x: float(x["score"]))

    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["raw_category", "mapped_category", "mapped_category_id", "score"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Source rows: {len(data)}")
    print(f"Unique raw categories: {len(cache)}")
    print(f"Output written: {TARGET_PRODUCTS_CSV}")
    print(f"Report written: {REPORT_CSV}")


if __name__ == "__main__":
    main()
