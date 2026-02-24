"""master@naver.com 계정을 users, user_health_profile 테이블에 추가"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from infra.db.session import SessionLocal

def main():
    db = SessionLocal()
    try:
        # 1) users
        db.execute(text("""
            INSERT INTO public.users (email, password_hash, created_at, updated_at, is_sensitive_agreed, agreed_at, is_tos_agreed, is_privacy_agreed)
            VALUES (
                'master@naver.com',
                '$2b$12$/fXxo9Fizr3VamqT5Uowu.BK73pPC1Ppqbg7WRw4egLnBUjpMf/7K',
                now(), now(), true, NULL, true, true
            )
        """))
        db.commit()

        # 2) user_health_profile (방금 생성된 user_id 사용)
        db.execute(text("""
            INSERT INTO public.user_health_profile (user_id, gender, birth_date, height, weight, average_of_steps, activity_level, diabetes, hypertension, kidneydisease, allergy, notes, favorite, goal)
            SELECT currval('public.users_user_id_seq'), 'F', '1993-02-25', 160.00, 50.00, 10000, '5', 'na', 'na', 'na', 'na', NULL, NULL, 'normal'
        """))
        db.commit()
        print("master@naver.com 계정이 users, user_health_profile 테이블에 추가되었습니다.")
    except Exception as e:
        db.rollback()
        print(f"오류: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
