"""users, user_health_profile 테이블 전체 조회"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from infra.db.session import SessionLocal

def main():
    db = SessionLocal()
    try:
        print("=" * 80)
        print("users 테이블")
        print("=" * 80)
        rows = db.execute(text("SELECT * FROM public.users ORDER BY user_id")).fetchall()
        cols = rows[0]._mapping.keys() if rows else []
        print(" | ".join(str(c) for c in cols))
        print("-" * 80)
        for r in rows:
            print(" | ".join(str(r._mapping[c]) for c in cols))

        print("\n" + "=" * 80)
        print("user_health_profile 테이블")
        print("=" * 80)
        rows = db.execute(text("SELECT * FROM public.user_health_profile ORDER BY user_id")).fetchall()
        cols = rows[0]._mapping.keys() if rows else []
        print(" | ".join(str(c) for c in cols))
        print("-" * 80)
        for r in rows:
            print(" | ".join(str(r._mapping[c]) for c in cols))
    finally:
        db.close()

if __name__ == "__main__":
    main()
