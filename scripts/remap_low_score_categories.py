import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
PRODUCTS_CSV = BASE_DIR / "infra" / "db" / "products.csv"
ORIGIN_PRODUCTS_CSV = BASE_DIR / "infra" / "db" / "products (1).csv"
CATEGORIES_CSV = BASE_DIR / "infra" / "db" / "categories.csv"
LOW_SCORE_REPORT_CSV = BASE_DIR / "infra" / "db" / "category_mapping_report.csv"
SECOND_REPORT_CSV = BASE_DIR / "infra" / "db" / "category_mapping_report_second_pass.csv"


def normalize(text: str) -> str:
    if text is None:
        return ""
    s = str(text).lower().strip()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", "", s)
    return s


def contains_any(text: str, keywords: list[str]) -> bool:
    n = normalize(text)
    return any(k in n for k in keywords)


def load_categories() -> dict[str, str]:
    categories = {}
    with CATEGORIES_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            cid = (row.get("category_id") or "").strip()
            if name and cid:
                categories[name] = cid
    return categories


def get_low_score_raw_categories() -> set[str]:
    lows = set()
    with LOW_SCORE_REPORT_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            try:
                score = float(row.get("score") or 0.0)
            except ValueError:
                score = 0.0
            if score < 0.5:
                lows.add((row.get("raw_category") or "").strip())
    return lows


def load_origin_raw_category_by_product_id() -> dict[str, str]:
    mapping = {}
    with ORIGIN_PRODUCTS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid = str(row.get("product_id") or "").strip()
            raw_cat = (row.get("카테고리") or "").strip()
            if pid:
                mapping[pid] = raw_cat
    return mapping


def rule_map(raw_category: str) -> str:
    raw = raw_category or ""

    # 1) 특정 타겟층 대상 식품은 기타식품류로 우선 매핑
    target_keywords = [
        "영아",
        "유아",
        "아동",
        "어린이",
        "청소년",
        "임산부",
        "수유부",
        "노인",
        "고령",
        "환자용",
        "환자",
        "선천성대사질환",
        "특수의료",
        "체중조절",
        "조제식",
    ]
    if contains_any(raw, target_keywords):
        return "기타식품류"

    # 2) 원료 오리진 우선 매핑
    if contains_any(raw, ["돼지", "소고기", "쇠고기", "닭", "축산", "햄", "소시지", "육", "포장육", "순대"]):
        return "식육가공품 및 포장육"
    if contains_any(raw, ["어묵", "어육", "수산", "생선", "참치", "새우", "게", "오징어", "어패", "해산", "해물"]):
        return "수산가공식품류"
    if contains_any(raw, ["난백", "난황", "전란", "계란", "알가공", "난가공"]):
        return "알가공품류"
    if contains_any(raw, ["치즈", "우유", "유가공", "요거트", "요구르트", "버터", "유청", "아이스크림", "아이스밀크", "샤베트"]):
        if contains_any(raw, ["아이스크림", "아이스밀크", "샤베트", "빙과"]):
            return "빙과류"
        return "유가공품류"
    if contains_any(raw, ["벌꿀", "꿀", "화분", "프로폴리스"]):
        return "벌꿀 및 화분가공품류"
    if contains_any(raw, ["곡물", "밀가루", "쌀", "보리", "감자", "고구마", "채소", "과채", "과일", "버섯", "견과", "두류", "농산"]):
        return "농산가공식품류"

    # 3) 가공방식 유사도 기반 매핑
    if contains_any(raw, ["절임", "장아찌", "피클", "조림", "정과"]):
        return "절임류 또는 조림류"
    if contains_any(raw, ["된장", "고추장", "간장", "청국장", "장류", "발효장"]):
        return "장류"
    if contains_any(raw, ["소스", "드레싱", "케첩", "마요네즈", "카레", "향신료", "조미", "시즈닝"]):
        return "조미식품"
    if contains_any(raw, ["라면", "면", "우동", "국수", "당면", "파스타", "쫄면"]):
        return "면류"
    if contains_any(raw, ["빵", "과자", "쿠키", "크래커", "떡", "시리얼"]):
        return "과자류·빵류 또는 떡류"
    if contains_any(raw, ["캔디", "켄디", "껌", "양갱", "캐러멜", "사탕", "당류", "시럽"]):
        return "당류"
    if contains_any(raw, ["초콜릿", "코코아"]):
        return "코코아가공품류 또는 초콜릿류"
    if contains_any(raw, ["잼", "마멀레이드"]):
        return "잼류"
    if contains_any(raw, ["두부", "묵"]):
        return "두부류 또는 묵류"
    if contains_any(raw, ["식용유", "기름", "유지", "쇼트닝", "마가린"]):
        return "식용유지류"
    if contains_any(raw, ["커피", "차", "음료", "주스", "드링크", "에이드", "탄산", "액상차", "고형차"]):
        return "음료류"
    if contains_any(raw, ["와인", "맥주", "소주", "리큐르", "주류", "전통주"]):
        return "주류"
    if contains_any(raw, ["즉석", "레토르트", "간편", "냉동식품", "hmr", "밀키트"]):
        return "즉석식품류"

    # Fallback: 카테고리명 유사도
    candidates = [
        "과자류·빵류 또는 떡류",
        "빙과류",
        "코코아가공품류 또는 초콜릿류",
        "당류",
        "잼류",
        "두부류 또는 묵류",
        "식용유지류",
        "면류",
        "음료류",
        "특수영양식품",
        "특수의료용도식품",
        "장류",
        "조미식품",
        "절임류 또는 조림류",
        "주류",
        "농산가공식품류",
        "식육가공품 및 포장육",
        "알가공품류",
        "유가공품류",
        "수산가공식품류",
        "동물성가공식품류",
        "벌꿀 및 화분가공품류",
        "즉석식품류",
        "기타식품류",
    ]
    best = "기타식품류"
    best_score = -1.0
    raw_n = normalize(raw)
    for cand in candidates:
        score = SequenceMatcher(None, raw_n, normalize(cand)).ratio()
        if score > best_score:
            best_score = score
            best = cand
    return best


def main() -> None:
    categories = load_categories()
    low_raw_categories = get_low_score_raw_categories()
    origin_category_by_pid = load_origin_raw_category_by_product_id()

    with PRODUCTS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if "category" not in fieldnames or "category_id" not in fieldnames:
        raise RuntimeError("products.csv must include category and category_id columns.")

    second_report_rows = []
    updated_rows = 0
    affected_raw_categories = set()

    for row in rows:
        pid = str(row.get("product_id") or "").strip()
        raw_cat = (origin_category_by_pid.get(pid) or "").strip()
        if raw_cat not in low_raw_categories:
            continue

        new_cat = rule_map(raw_cat)
        new_cat_id = categories.get(new_cat, "pf24")
        old_cat = (row.get("category") or "").strip()
        old_cat_id = (row.get("category_id") or "").strip()

        row["category"] = new_cat
        row["category_id"] = new_cat_id
        updated_rows += 1
        affected_raw_categories.add(raw_cat)

        second_report_rows.append(
            {
                "product_id": pid,
                "raw_category": raw_cat,
                "old_mapped_category": old_cat,
                "old_mapped_category_id": old_cat_id,
                "new_mapped_category": new_cat,
                "new_mapped_category_id": new_cat_id,
            }
        )

    with PRODUCTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    with SECOND_REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "product_id",
                "raw_category",
                "old_mapped_category",
                "old_mapped_category_id",
                "new_mapped_category",
                "new_mapped_category_id",
            ],
        )
        writer.writeheader()
        writer.writerows(second_report_rows)

    print(f"Low-score raw categories: {len(low_raw_categories)}")
    print(f"Affected raw categories in products: {len(affected_raw_categories)}")
    print(f"Updated product rows: {updated_rows}")
    print(f"Second-pass report written: {SECOND_REPORT_CSV}")


if __name__ == "__main__":
    main()
