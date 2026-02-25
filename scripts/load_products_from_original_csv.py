import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text

CSV_PATH = "products_ver2.csv"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://appuser:apppassword@localhost:5432/appdb",
)

def read_csv_korean_safe(path: str) -> pd.DataFrame:
    # 한글 깨짐 방지: utf-8-sig -> utf-8 -> cp949 -> euc-kr 순으로 시도
    for enc in ["utf-8-sig", "utf-8", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            pass
    # 마지막 fallback
    return pd.read_csv(path)

def clean_str(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    s = s.replace({"nan": None, "NaN": None, "None": None, "": None})
    return s

def to_int(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").astype("Int64")

def to_num(s: pd.Series) -> pd.Series:
    # 소수점 포함 numeric 유지
    return pd.to_numeric(s, errors="coerce")

def pick(df: pd.DataFrame, candidates: list[str], unnamed_prefix: str | None = None) -> pd.Series:
    for c in candidates:
        if c in df.columns:
            return df[c]
    if unnamed_prefix:
        m = [c for c in df.columns if str(c).startswith(unnamed_prefix)]
        if m:
            return df[m[0]]
    return pd.Series([None] * len(df))

def to_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return True
    s = str(x).strip().lower()
    if s in ["1", "true", "t", "y", "yes", "활성", "on"]:
        return True
    if s in ["0", "false", "f", "n", "no", "비활성", "off"]:
        return False
    return True

def main():
    df = read_csv_korean_safe(CSV_PATH)
    df.columns = [str(c).strip().replace("\ufeff", "") for c in df.columns]

    # ✅ 너가 말했던 매핑 fallback 포함
    pid = pick(df, ["product_id", "ProductID", "상품ID", "상품아이디"], unnamed_prefix="Unnamed: 13")
    img = pick(df, ["img_url", "image_url", "imageUrl", "이미지url", "이미지_url"], unnamed_prefix="Unnamed: 3")

    payload = pd.DataFrame({
        "product_id": to_int(pid),
        "name": clean_str(pick(df, ["제품명", "상품명", "name"])),
        "brand": clean_str(pick(df, ["제조사", "브랜드", "brand"])),
        "category_id": to_int(pick(df, ["category_id", "카테고리ID", "카테고리_id"])),
        "image_url": clean_str(img),

        "is_active": pick(df, ["is_active", "활성", "active"]).apply(to_bool),
        "quantity": to_int(pick(df, ["quantity", "수량", "재고"])).fillna(0),

        "rawmtrl": clean_str(pick(df, ["원재료", "식품원재료", "rawmtrl"])),
        "allergymtrl": clean_str(pick(df, ["알러지", "알레르기", "allergymtrl"])),

        # 영양성분(소수점 유지)
        "kcal": to_num(pick(df, ["에너지(kcal)", "kcal", "에너지"])),
        "protein_g": to_num(pick(df, ["단백질(g)", "protein_g"])),
        "fat_g": to_num(pick(df, ["지방(g)", "fat_g"])),
        "ash_g": to_num(pick(df, ["회분(g)", "ash_g"])),
        "carb_g": to_num(pick(df, ["탄수화물(g)", "carb_g"])),
        "sugar_g": to_num(pick(df, ["당류(g)", "sugar_g"])),
        "sodium_mg": to_num(pick(df, ["나트륨(mg)", "sodium_mg"])),
        "cholesterol_mg": to_num(pick(df, ["콜레스테롤(mg)", "cholesterol_mg"])),
        "sat_fat_g": to_num(pick(df, ["포화지방산(g)", "sat_fat_g"])),
        "trans_fat_g": to_num(pick(df, ["트랜스지방산(g)", "trans_fat_g"])),

        "nutrient_basis_g": to_num(pick(df, ["영양성분함량기준량", "nutrient_basis_g"])),
        "serving_ref_g": to_num(pick(df, ["1회섭취참고량", "serving_ref_g"])),
        "food_weight_g": to_num(pick(df, ["식품중량", "food_weight_g"])),

        "gi": to_num(pick(df, ["gi", "GI"])),
        "gl": to_num(pick(df, ["gl", "GL"])),
    })

    # 필수값 없는 row 제거 (DB NOT NULL 보호)
    payload = payload.dropna(subset=["product_id", "name", "brand"])

    # product_id 중복 있으면 마지막 값으로 덮어쓰기 (업서트랑 궁합 좋게)
    payload = payload.sort_values("product_id").drop_duplicates(subset=["product_id"], keep="last")

    # pandas NaN -> python None
    records = payload.where(pd.notnull(payload), None).to_dict(orient="records")

    engine = create_engine(DATABASE_URL, future=True)

    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO products (
                    product_id, name, brand, category_id, image_url,
                    is_active, quantity,
                    rawmtrl, allergymtrl,
                    kcal, protein_g, fat_g, ash_g, carb_g, sugar_g, sodium_mg,
                    cholesterol_mg, sat_fat_g, trans_fat_g,
                    nutrient_basis_g, serving_ref_g, food_weight_g,
                    gi, gl
                )
                VALUES (
                    :product_id, :name, :brand, :category_id, :image_url,
                    :is_active, :quantity,
                    :rawmtrl, :allergymtrl,
                    :kcal, :protein_g, :fat_g, :ash_g, :carb_g, :sugar_g, :sodium_mg,
                    :cholesterol_mg, :sat_fat_g, :trans_fat_g,
                    :nutrient_basis_g, :serving_ref_g, :food_weight_g,
                    :gi, :gl
                )
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    brand = EXCLUDED.brand,
                    category_id = EXCLUDED.category_id,
                    image_url = EXCLUDED.image_url,
                    is_active = EXCLUDED.is_active,
                    quantity = EXCLUDED.quantity,
                    rawmtrl = EXCLUDED.rawmtrl,
                    allergymtrl = EXCLUDED.allergymtrl,
                    kcal = EXCLUDED.kcal,
                    protein_g = EXCLUDED.protein_g,
                    fat_g = EXCLUDED.fat_g,
                    ash_g = EXCLUDED.ash_g,
                    carb_g = EXCLUDED.carb_g,
                    sugar_g = EXCLUDED.sugar_g,
                    sodium_mg = EXCLUDED.sodium_mg,
                    cholesterol_mg = EXCLUDED.cholesterol_mg,
                    sat_fat_g = EXCLUDED.sat_fat_g,
                    trans_fat_g = EXCLUDED.trans_fat_g,
                    nutrient_basis_g = EXCLUDED.nutrient_basis_g,
                    serving_ref_g = EXCLUDED.serving_ref_g,
                    food_weight_g = EXCLUDED.food_weight_g,
                    gi = EXCLUDED.gi,
                    gl = EXCLUDED.gl,
                    updated_at = now();
            """),
            records
        )

        # 시퀀스 꼬임 방지
        conn.execute(text("""
            SELECT setval('products_product_id_seq',
                          (SELECT COALESCE(MAX(product_id), 1) FROM products));
        """))

    print(f"✅ inserted/updated rows: {len(records)}")

if __name__ == "__main__":
    main()