import csv
import re
from difflib import SequenceMatcher
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
CATEGORIES_CSV = BASE_DIR / "infra" / "db" / "categories.csv"
PRODUCTS_CSV = BASE_DIR / "infra" / "db" / "products.csv"
PRODUCTS_OUT_CSV = BASE_DIR / "infra" / "db" / "products.remapped.csv"
REPORT_CSV = BASE_DIR / "infra" / "db" / "category_mapping_report.csv"


def normalize(text: str) -> str:
    if text is None:
        return ""
    s = str(text).strip().lower()
    s = re.sub(r"\([^)]*\)", " ", s)
    s = s.replace("·", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", "", s)
    s = s.replace("식품", "")
    s = s.replace("가공품", "")
    s = s.replace("가공", "")
    s = s.replace("제품", "")
    s = s.replace("류", "")
    return s


def token_set(text: str) -> set[str]:
    if text is None:
        return set()
    s = str(text).strip().lower()
    s = s.replace("·", " ")
    s = re.sub(r"[^\w\s]", " ", s)
    tokens = {t for t in re.split(r"\s+", s) if t}
    cleaned = set()
    for tok in tokens:
        tok = tok.replace("식품", "").replace("가공품", "").replace("가공", "").replace("제품", "")
        tok = tok.replace("류", "")
        if tok:
            cleaned.add(tok)
    return cleaned


def score_match(src: str, target: str) -> float:
    src_n = normalize(src)
    tgt_n = normalize(target)
    if not src_n or not tgt_n:
        return 0.0

    ratio = SequenceMatcher(None, src_n, tgt_n).ratio()

    src_tokens = token_set(src)
    tgt_tokens = token_set(target)
    if src_tokens or tgt_tokens:
        jaccard = len(src_tokens & tgt_tokens) / max(len(src_tokens | tgt_tokens), 1)
    else:
        jaccard = 0.0

    contains_bonus = 0.0
    if src_n in tgt_n or tgt_n in src_n:
        contains_bonus = 0.08

    return ratio * 0.7 + jaccard * 0.3 + contains_bonus


def read_categories() -> list[dict]:
    rows = []
    with CATEGORIES_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "category_id": (row.get("category_id") or "").strip(),
                    "name": (row.get("name") or "").strip(),
                    "supercategory": (row.get("supercategory") or "").strip(),
                }
            )
    return [r for r in rows if r["category_id"] and r["name"]]


def pick_best_category(raw_category: str, categories: list[dict]) -> dict:
    best = None
    best_score = -1.0
    for c in categories:
        s = score_match(raw_category, c["name"])
        if s > best_score:
            best_score = s
            best = c
    return {"best": best, "score": best_score}


def main() -> None:
    categories = read_categories()

    with PRODUCTS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        source_fieldnames = reader.fieldnames or []
        rows = list(reader)

    if "category" in source_fieldnames:
        source_category_col = "category"
    else:
        source_category_col = next(
            (c for c in source_fieldnames if "category" in c.lower()),
            None,
        )

    if not source_category_col:
        raise RuntimeError("No category-like column found in products.csv")

    out_fieldnames = []
    inserted = False
    for col in source_fieldnames:
        if col == source_category_col:
            out_fieldnames.extend(["category", "category_id"])
            inserted = True
        else:
            out_fieldnames.append(col)
    if not inserted:
        out_fieldnames.extend(["category", "category_id"])

    cache: dict[str, tuple[str, str, float]] = {}
    report_rows: list[dict] = []

    for row in rows:
        raw_cat = (row.get(source_category_col) or "").strip()
        if raw_cat not in cache:
            picked = pick_best_category(raw_cat, categories)
            best = picked["best"] or {"name": "", "category_id": ""}
            cache[raw_cat] = (best["name"], best["category_id"], round(picked["score"], 4))

            report_rows.append(
                {
                    "raw_category": raw_cat,
                    "mapped_category": best["name"],
                    "mapped_category_id": best["category_id"],
                    "score": round(picked["score"], 4),
                }
            )

        mapped_name, mapped_id, _ = cache[raw_cat]
        row["category"] = mapped_name
        row["category_id"] = mapped_id
        if source_category_col != "category":
            row.pop(source_category_col, None)

    write_target = PRODUCTS_CSV
    wrote_fallback = False
    try:
        with PRODUCTS_CSV.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    except PermissionError:
        write_target = PRODUCTS_OUT_CSV
        wrote_fallback = True
        with PRODUCTS_OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    report_rows.sort(key=lambda x: x["score"])
    with REPORT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["raw_category", "mapped_category", "mapped_category_id", "score"],
        )
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Total products: {len(rows)}")
    print(f"Unique raw categories: {len(cache)}")
    print(f"Source category column: {source_category_col}")
    print(f"Products written: {write_target}")
    if wrote_fallback:
        print("products.csv is locked; wrote fallback file instead.")
    print(f"Report written: {REPORT_CSV}")
    print("Lowest 15 match scores:")
    for item in report_rows[:15]:
        print(
            f"- {item['raw_category']} -> {item['mapped_category']} "
            f"({item['mapped_category_id']}) score={item['score']}"
        )


if __name__ == "__main__":
    main()
