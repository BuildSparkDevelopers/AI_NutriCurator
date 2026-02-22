# infra/db/repositories/product_repo.py
# # 역할: 상품 저장소 접근(CRUD/조회)만 담당
# # - 비즈니스 규칙(필터링 정책, 응답 형태)은 service에서 처리

from typing import Optional, List, Dict
from infra.db.store import InMemoryStore


# ✅ MVP seed 데이터 (팀원 데이터 그대로)
DEMO_PRODUCTS: Dict[str, dict] = {
  "0": {
    "product_id": "201905000000",
    "name": "설화눈꽃팝김부각스낵",
    "brand": "설화",
    "category": "과자",
    "ingredients": ["찹쌀", "김", "참깨", "옥수수기름", "양파", "무", "대파", "천일염", "마늘", "새우", "멸치", "다시마", "건표고버섯", "둥굴레", "감초", "정제수"],
    "allergy": "없음",
    "trace": "null",
    "calories": 150,
    "sodium": 180,
    "carbohydrate": 20,
    "sugar": 1,
    "fat": 7,
    "trans_fat": 0,
    "saturated_fat": 1.2,
    "cholesterol": 5,
    "protein": 2,
    "phosphorus": 45,
    "calcium": 30,
    "potassium": 120,
    "inferred_types": ["low_sugar"]
  },
  "1": {
    "product_id": "201804000001",
    "name": "설화눈꽃팝김부각스낵 아몬드맛",
    "brand": "설화",
    "category": "과자",
    "ingredients": ["찹쌀", "김", "참깨", "아몬드", "양파", "무", "천일염", "새우", "멸치", "다시마", "정제수"],
    "allergy": "아몬드",
    "trace": "",
    "calories": 170,
    "sodium": 160,
    "carbohydrate": 18,
    "sugar": 1,
    "fat": 10,
    "trans_fat": 0,
    "saturated_fat": 1.0,
    "cholesterol": 3,
    "protein": 4,
    "phosphorus": 80,
    "calcium": 50,
    "potassium": 200,
    "inferred_types": ["low_sugar"]
  },
  "2": {
    "product_id": "201804000002",
    "name": "고들빼기김치",
    "brand": "남도미가",
    "category": "김치류",
    "ingredients": ["고들빼기", "멸치액", "염장새우", "양파", "혼합간장", "고춧가루", "마늘", "참깨", "물엿", "배즙", "당근"],
    "allergy": "새우,대두,밀",
    "trace": "밀, 땅콩, 복숭아, 토마토, 호두, 아황산류 혼입 가능",
    "calories": 45,
    "sodium": 850,
    "carbohydrate": 8,
    "sugar": 4,
    "fat": 0.5,
    "trans_fat": 0,
    "saturated_fat": 0.1,
    "cholesterol": 2,
    "protein": 2,
    "phosphorus": 35,
    "calcium": 40,
    "potassium": 320,
    "inferred_types": ["low_fat", "low_sugar", "high_sodium"]
  },
  "3": {
    "product_id": "199504000000",
    "name": "해태 허니버터칩",
    "brand": "해태",
    "category": "과자",
    "ingredients": ["감자", "혼합식용유", "허니버터맛시즈닝", "탈지분유(우유)", "버터혼합분말(대두)", "아카시아꿀", "고메버터(밀)"],
    "allergy": "알수없음",
    "trace": "null",
    "calories": 345,
    "sodium": 350,
    "carbohydrate": 30,
    "sugar": 7,
    "fat": 23,
    "trans_fat": 0.1,
    "saturated_fat": 8,
    "cholesterol": 10,
    "protein": 3,
    "phosphorus": 70,
    "calcium": 25,
    "potassium": 450,
    "inferred_types": ["high_fat"]
  },
  "4": {
    "product_id": "201405000000",
    "name": "헬로버블 라이스퍼프 양파맛",
    "brand": "헬로버블",
    "category": "유아간식",
    "ingredients": ["현미", "어니언시즈닝", "정백당", "리치버터분말", "양파분", "합성향료", "백미", "옥수수과립"],
    "allergy": "알수없음",
    "trace": "돼지고기, 땅콩, 복숭아, 아황산류, 호두 혼입 가능",
    "calories": 120,
    "sodium": 110,
    "carbohydrate": 22,
    "sugar": 3,
    "fat": 2.5,
    "trans_fat": 0,
    "saturated_fat": 0.5,
    "cholesterol": 0,
    "protein": 2,
    "phosphorus": 55,
    "calcium": 15,
    "potassium": 90,
    "inferred_types": ["low_fat", "low_sugar", "low_sodium"]
  },
  "5": {
    "product_id": "201105000000",
    "name": "두마리목장 콜비치즈",
    "brand": "두마리목장",
    "category": "치즈/유제품",
    "ingredients": ["원유(국산)99.9%", "우유응고효소", "유산균", "식염", "안나토색소"],
    "allergy": "우유함유",
    "trace": "null",
    "calories": 115,
    "sodium": 190,
    "carbohydrate": 1,
    "sugar": 0.5,
    "fat": 9,
    "trans_fat": 0.3,
    "saturated_fat": 6,
    "cholesterol": 30,
    "protein": 7,
    "phosphorus": 140,
    "calcium": 210,
    "potassium": 25,
    "inferred_types": ["low_sugar"]
  },
  "6": {
    "product_id": "201105000001",
    "name": "양반 바삭 튀김가루",
    "brand": "양반",
    "category": "가루/조미료",
    "ingredients": ["밀가루", "변성전분", "베이킹파우더", "정제소금", "양파분말", "옥수수가루"],
    "allergy": "밀",
    "trace": "null",
    "calories": 350,
    "sodium": 650,
    "carbohydrate": 78,
    "sugar": 2,
    "fat": 1.2,
    "trans_fat": 0,
    "saturated_fat": 0.3,
    "cholesterol": 0,
    "protein": 7,
    "phosphorus": 95,
    "calcium": 20,
    "potassium": 110,
    "inferred_types": ["low_fat", "low_sugar", "high_carb", "high_sodium"]
  },
  "7": {
    "product_id": "201104000001",
    "name": "돈목살훈제바베큐스테이크",
    "brand": "옐로우팜",
    "category": "가공육",
    "ingredients": ["돼지고기 96.68%", "스모크시즈닝", "분리대두단백", "토마토케찹", "아질산나트륨"],
    "allergy": "돼지고기,밀,우유,대두,쇠고기,토마토 함유",
    "trace": "null",
    "calories": 280,
    "sodium": 720,
    "carbohydrate": 5,
    "sugar": 2,
    "fat": 20,
    "trans_fat": 0,
    "saturated_fat": 7,
    "cholesterol": 65,
    "protein": 19,
    "phosphorus": 180,
    "calcium": 15,
    "potassium": 310,
    "inferred_types": ["low_sugar", "high_protein", "high_fat", "high_sodium"]
  },
  "8": {
    "product_id": "201104000002",
    "name": "태양초 고추장 골드",
    "brand": "해찬들",
    "category": "장류",
    "ingredients": ["고춧가루", "물엿", "소맥분(밀)", "혼합양념", "밀쌀", "정제소금", "정백당"],
    "allergy": "알수없음",
    "trace": "null",
    "calories": 210,
    "sodium": 2400,
    "carbohydrate": 48,
    "sugar": 25,
    "fat": 1,
    "trans_fat": 0,
    "saturated_fat": 0.2,
    "cholesterol": 0,
    "protein": 4,
    "phosphorus": 90,
    "calcium": 35,
    "potassium": 450,
    "inferred_types": ["low_fat", "high_sugar", "high_sodium"]
  },
  "9": {
    "product_id": "201104000003",
    "name": "환타지 믹스너트",
    "brand": "환타지",
    "category": "견과류",
    "ingredients": ["커피땅콩", "화이트볼", "찹쌀땅콩", "튀김땅콩", "로스티드피너츠", "바나나칩", "볶음아몬드", "꿀땅콩"],
    "allergy": "알수없음",
    "trace": "null",
    "calories": 520,
    "sodium": 280,
    "carbohydrate": 45,
    "sugar": 18,
    "fat": 34,
    "trans_fat": 0,
    "saturated_fat": 9,
    "cholesterol": 0,
    "protein": 14,
    "phosphorus": 310,
    "calcium": 75,
    "potassium": 580,
    "inferred_types": ["high_sugar", "high_protein", "high_fat", "high_potassium"]
  }
}


class ProductRepository:
    def __init__(self, db: InMemoryStore):
        self.db = db

    def get_by_id(self, product_id: str) -> Optional[dict]:
        # ✅ product_id는 문자열로 통일 (ex: "201905000000")
        return self.db.products.get(str(product_id))

    def list_all(self) -> List[dict]:
        return list(self.db.products.values())

    def seed_if_empty(self) -> None:
        # # 역할: MVP 테스트용 seed 데이터 (비어있을 때만 주입)
        if self.db.products:
            return

        # ✅ demo는 {"0": {...}, "1": {...}} 형태라서 values() 또는 items()로 돌기
        for p in DEMO_PRODUCTS.values():
            pid = str(p["product_id"])
            self.db.products[pid] = p
