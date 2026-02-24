"""user_id 1~20 계정 비밀번호를 이메일 @ 앞 부분으로 bcrypt 해시 후 업데이트"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from passlib.context import CryptContext
from sqlalchemy import text
from infra.db.session import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    db = SessionLocal()
    try:
        rows = db.execute(text(
            "SELECT user_id, email FROM public.users WHERE user_id BETWEEN 1 AND 20"
        )).fetchall()

        for r in rows:
            user_id = r._mapping["user_id"]
            email = r._mapping["email"]
            password = email.split("@")[0]  # @ 앞 부분
            password_hash = pwd_context.hash(password)

            db.execute(text("""
                UPDATE public.users
                SET password_hash = :hash
                WHERE user_id = :uid
            """), {"hash": password_hash, "uid": user_id})
            print(f"user_id {user_id}: {email} -> 비밀번호 '{password}' (bcrypt) 적용")

        db.commit()
        print(f"\n총 {len(rows)}건 업데이트 완료.")
    except Exception as e:
        db.rollback()
        print(f"오류: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
