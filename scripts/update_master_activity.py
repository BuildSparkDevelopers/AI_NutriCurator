"""master@naver.com 계정의 activity_level을 5로 수정"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from infra.db.session import SessionLocal

def main():
    db = SessionLocal()
    try:
        result = db.execute(text("""
            UPDATE public.user_health_profile
            SET activity_level = '5'
            WHERE user_id = (SELECT user_id FROM public.users WHERE email = 'master@naver.com')
        """))
        db.commit()
        print(f"master@naver.com activity_level이 5로 수정되었습니다. (영향받은 행: {result.rowcount})")
    except Exception as e:
        db.rollback()
        print(f"오류: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
