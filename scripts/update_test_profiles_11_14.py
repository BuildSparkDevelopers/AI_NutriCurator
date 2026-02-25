"""user_id 11~14를 단일 질병 테스트 계정으로 user_health_profile 업데이트/생성

- user_id 11: 당뇨 type1 (나머지 na)
- user_id 12: 고혈압 stage1 (나머지 na)
- user_id 13: 신장질환 HD (혈액투석)
- user_id 14: 알러지 milk (나머지 na)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from infra.db.session import SessionLocal

# 각 user_id별 프로필 (질병 1개만, 나머지 na)
PROFILES = [
    {
        "user_id": 11,
        "gender": "M",
        "birth_date": "1995-03-15",
        "height": 175.00,
        "weight": 72.00,
        "average_of_steps": 7500,
        "activity_level": "3_4",
        "diabetes": "type1",
        "hypertension": "na",
        "kidneydisease": "na",
        "allergy": [],
        "notes": "테스트: 당뇨 type1만",
        "favorite": "grilled",
        "goal": "normal",
    },
    {
        "user_id": 12,
        "gender": "F",
        "birth_date": "1992-07-22",
        "height": 162.00,
        "weight": 58.00,
        "average_of_steps": 6000,
        "activity_level": "1_2",
        "diabetes": "na",
        "hypertension": "stage1",
        "kidneydisease": "na",
        "allergy": [],
        "notes": "테스트: 고혈압 stage1만",
        "favorite": "salad",
        "goal": "normal",
    },
    {
        "user_id": 13,
        "gender": "M",
        "birth_date": "1988-11-08",
        "height": 170.00,
        "weight": 68.00,
        "average_of_steps": 4000,
        "activity_level": "1_2",
        "diabetes": "na",
        "hypertension": "na",
        "kidneydisease": "HD",
        "allergy": [],
        "notes": "테스트: 신장질환 HD(혈액투석)만",
        "favorite": "soup",
        "goal": "patient",
    },
    {
        "user_id": 14,
        "gender": "F",
        "birth_date": "1997-04-30",
        "height": 165.00,
        "weight": 55.00,
        "average_of_steps": 9000,
        "activity_level": "5_7",
        "diabetes": "na",
        "hypertension": "na",
        "kidneydisease": "na",
        "allergy": ["MILK"],
        "notes": "테스트: 알러지 milk만",
        "favorite": "fruit",
        "goal": "normal",
    },
]

def main():
    db = SessionLocal()
    try:
        for p in PROFILES:
            db.execute(text("""
                INSERT INTO public.user_health_profile (
                    user_id, gender, birth_date, height, weight, average_of_steps,
                    activity_level, diabetes, hypertension, kidneydisease, allergy,
                    notes, favorite, goal
                ) VALUES (
                    :user_id, :gender, CAST(:birth_date AS date), :height, :weight, :average_of_steps,
                    :activity_level, CAST(:diabetes AS diabetes_enum), CAST(:hypertension AS hypertension_enum),
                    CAST(:kidneydisease AS kidneydisease_enum), CAST(:allergy AS allergy_enum[]),
                    :notes, :favorite, :goal
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    gender = EXCLUDED.gender,
                    birth_date = EXCLUDED.birth_date,
                    height = EXCLUDED.height,
                    weight = EXCLUDED.weight,
                    average_of_steps = EXCLUDED.average_of_steps,
                    activity_level = EXCLUDED.activity_level,
                    diabetes = EXCLUDED.diabetes,
                    hypertension = EXCLUDED.hypertension,
                    kidneydisease = EXCLUDED.kidneydisease,
                    allergy = EXCLUDED.allergy,
                    notes = EXCLUDED.notes,
                    favorite = EXCLUDED.favorite,
                    goal = EXCLUDED.goal
            """), p)
            print(f"user_id {p['user_id']}: {p['diabetes']}/{p['hypertension']}/{p['kidneydisease']}/{p['allergy']} 적용")

        db.commit()
        print("\n총 4건 적용 완료.")
    except Exception as e:
        db.rollback()
        print(f"오류: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
