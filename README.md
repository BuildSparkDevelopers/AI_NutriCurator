# 📄📢 AI-NutriCurator

만성질환 중증도 환자들은 일상적인 커머스 환경에서도 본인의 건강 상태에 적합한 식품을 선택하는 데 정보의 비대칭성 및 상품 탐색 과정에서의 불편함을 겪고 있습니다. 
본 AI서비스는 신뢰도 높은 출처 기반으로 구축된 DB를 바탕으로 정확도 높은 메세지 생성 및 추천 로직을 통해 이를 해소하고자 합니다.

## Team BuildSparkDevelopers

팀장: 소형선 이영주 박수빈

## 🚀 주요 기능

- **사용자 프로필 관리**: 알러지 정보 및 건강 제한사항 관리
- **제품 알러지 분석**: 22종 식약처 고시 알레르기 유발 물질 기준 분석
- **대체재 추천**: 알러지 성분에 대한 안전한 대체 식재료 추천
- **실시간 검색**: 제품명 및 원재료 기반 검색 기능
- **안전성 평가**: 제품 섭취 가능 여부 및 위험도 평가

## 📦 프로젝트 구조

```
AI-NutriCurator/
├── backend/
│   └── app.py              # FastAPI 백엔드 서버
├── index.html              # 프론트엔드 웹 인터페이스
├── requirements.txt        # Python 의존성
├── package.json           # Node.js 의존성 (선택사항)
└── agent_chat_allergy(완).py  # AI 모델 통합 스크립트
```

## 🛠️ 설치 및 실행

### 1. Python 환경 설정

```bash
# Python 가상환경 생성 (선택사항)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 백엔드 서버 실행

```bash
cd backend
python app.py
```

또는 uvicorn 직접 실행:

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 3. 프론트엔드 실행

프론트엔드는 정적 HTML 파일이므로 다음 방법 중 하나로 실행할 수 있습니다:

**방법 1: 라이브 서버 (VSCode 확장)**
- VSCode에서 `index.html` 파일을 열고 "Go Live" 클릭

**방법 2: Python 간단 서버**
```bash
python -m http.server 3000
```

**방법 3: 브라우저에서 직접 열기**
```bash
# index.html 파일을 브라우저로 드래그 앤 드롭
```

프론트엔드는 `http://localhost:3000` 또는 직접 열어서 접근합니다.

## 📡 API 엔드포인트

### 제품 관련
- `GET /products` - 전체 제품 목록 조회
- `GET /products/{product_id}` - 특정 제품 상세 조회
- `GET /search?q={query}` - 제품 검색

### 프로필 관련
- `GET /profiles` - 사용자 프로필 목록 조회
- `GET /profiles/{profile_id}` - 특정 프로필 조회

### 분석
- `POST /analyze` - 제품 알러지 분석
  ```json
  {
    "product_id": "0",
    "profile_id": "0"
  }
  ```

## 🎨 사용 방법

1. **프로필 선택**: 상단에서 자신의 건강 상태에 맞는 프로필을 선택합니다.
2. **제품 검색**: 검색창에 제품명이나 원재료를 입력하여 제품을 찾습니다.
3. **알러지 분석**: 제품 카드의 "알러지 분석" 버튼을 클릭합니다.
4. **결과 확인**: 
   - ✅ **안전**: 알러지 성분이 검출되지 않음
   - ⚠️ **주의**: 교차오염 가능성 있음
   - ❌ **위험**: 알러지 성분 포함, 섭취 금지

## 🔧 기술 스택

### 백엔드
- **FastAPI**: 고성능 Python 웹 프레임워크
- **Pydantic**: 데이터 검증
- **Uvicorn**: ASGI 서버

### 프론트엔드
- **HTML5 / CSS3 / JavaScript (Vanilla)**
- **Tailwind CSS**: 스타일링
- **Font Awesome**: 아이콘

### AI/ML (선택사항)
- **PyTorch**: 딥러닝 프레임워크
- **Transformers**: 사전 학습 모델 (Qwen2.5)

## 📊 데이터베이스

현재는 인메모리 데이터를 사용하고 있습니다. 프로덕션 환경에서는 다음을 고려하세요:

- PostgreSQL / MySQL
- MongoDB (문서 기반)
- SQLite (개발/테스트)

## 🔐 보안 고려사항

- API 인증/인가 구현 필요
- HTTPS 사용 권장
- 입력 데이터 검증
- SQL Injection 방지
- XSS 공격 방지

## 🚧 향후 개발 계획

- [ ] 사용자 계정 및 인증 시스템
- [ ] 데이터베이스 통합
- [ ] 실제 AI 모델 통합 (Qwen2.5)
- [ ] 제품 바코드 스캔 기능
- [ ] 영양 성분 분석
- [ ] 개인화된 식단 추천
- [ ] 모바일 앱 개발

## 📝 라이센스

MIT License

## 👥 기여자

- 소형선 (팀장)
- 이영주
- 박수빈

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 등록해주세요.

---

**⚠️ 면책 조항**: 이 시스템은 보조 도구이며, 실제 의료 조언을 대체할 수 없습니다. 심각한 알러지가 있는 경우 반드시 전문의와 상담하세요.
# 📄📢 사용법/실행법/팀 규칙 정리

#
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#

# 🤖 에이전트 개요


START: 유저가 [장바구니 담기] 버튼을 클릭함

## 1️⃣ Node 1 (Orch-01): Eligibility Checking & Routing (Conditional Edge)

### 1. 유저가 질병을 보유하고 있는가?
*@USER-Agent 호출
* IN: USER-01의 Profile Retrieval
* Logic : PASS or WARN

      disease = diabetes + hypertension + kidneydisease + allergy

          ** PASS: disease = 0    -> end
          ** WARN: disease >= 1   -> 2. 이동


### 2. 식품에 유관 성분이 있는가?
*@CHAT-Agent 호출
* IN: CHAT-01의 Evidence Generation
* logic : PASS or WARN

          ** PASS: 부적합성분 없음    -> end,
          ** WARN: 부적합성분 있음    -> to_chat, to_reco

* next: 판정결과에 따라 다른 에이전트 및 tool 호출, 상품특성 JSON 전달

#
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#

## 2️⃣ Node 2 (User-01): Profile Retrieval

유저프로필을 조회하여 건강정보 확인 및 페르소나를 JSON 출력
* MVP: ?user_id?, weight, diabetes, hypertension, kidneydisease, allergy
* Post-MVP: height, activity_level, persona(FK, Post-MVP DB)



### 참고) final_profile DB
Node2(User-02) + priority_map + 유관성분 임계값&문자열 필터링
* 미리 생성해서 DB에 저장된 상태

Logic :
* 임계값 기반 필터링

      diabetes: (-)당(<5g)
                (+)식이섬유(>=14g/1,000kcal)

      hypertension: (-)나트륨(<2,300mg/day),
                    (-)칼륨 > 3500mg
                    (-)총 지방 < 하루 총 열량의 20-25% 이하

      kidneydisease:  CKD 3-5단계 (투석 전, 당뇨 없음)
                      (-)단백질 kg당 0.55-0.60g/kg/일
                      (-)나트륨 2.3g 미만
                      (-)인 800-1,000 mg/일
                      (-)칼슘 800-1,000mg/일
                      (-)25-35 kcal/kg/일

                      CKD 5단계 (투석)
                      (+)단백질 1.0-1.2g/kg/일
                      (-)나트륨 2.3g 미만
                      (-)칼륨 2,000/일로 제한
                      (-)인 800-1,000 mg/일
                      (-)칼슘 800-1,000mg/일
                      (-)25-35 kcal/kg/일
      
      (POST-MVP에서는 (+) 성분 섭취시 긍정피드백을 주는것도 고려)

* 문자열 기반 필터링

      allergy: 우유, 달걀, 땅콩, 견과류, 콩, 밀, 생선, 갑각류 어패류
      원재료 포함성분 및 교차오염성분

* 우선순위 순으로

      priority_map = { allergy: 1, kidneydisease: 2, diabetes : 3, hypertension: 4 }

          질병 우선순위에 따른 필터링성분 및 임계값을 먼저 호출.
          그 다음 순위 질병의 필터링성분을 호출
          -> 이미 호출된 필터링성분은 새로 호출하지 않음
          Priority-Merger -> 질병 우선순위에 따라 Final_Profile 생성

      final_profile = {
          user_id: ,
          성분1: 성분1함량,
          성분2: 성분2함량,
          알러지: 알러젠
          ...

#
# ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ
#

## 3️⃣ Node 3 (Chat-01): Evidence Generation

식품성분과 질환 가이드라인을 대조하여 근거기반 적합성 판별후 *JSON 출력*
* IN: final_profile DB, product DB, disease RAG?

      *final_profile DB:
      *product DB: product_id, name, category, brand
                -> 성분함량체크 및 상품 조회 맥락 유지
      *disease RAG: 질병유관 성분 및 성분 가이드(함량)
                -> 식품 성분 적합성
* logic : 질환별 성분 필터링 (simple check)

* 판단결과 예시 ----> **JSON 기반으로 변경 필요

      Scenario : 🚫 영양 성분 초과 (Nutrient Violation)
        - 최종 판정: [WARN]
        - 위반 알러지: []
        - 위반 영양소: ['sodium', 'sugar']
        - 상세 리포트:
          ✅ PROTEIN: 실제 15.0 / 기준 40.0
          🚩 SODIUM: 실제 3000.0 / 기준 2300.0
          🚩 SUGAR: 실제 10.0 / 기준 5.0



## 4️⃣ Node 4 (Reco-01): Vector DB Search & Recommendation

* 상품특성 JSON을 받아서 유사한 상품 조회 및 추천

## 4️⃣ Node 4-1 (sub-Reco-01): Vector DB Search & Recommendation

방식1: 레코에서 준 30-50개 정도의 상품중에서 roles.py 로 3개를 추천
방식2: 레코에서는 3개만 주고 그 3개 상품의 조회맥락과 식품성분이 유저에게 맞는지 판단

## 5️⃣ Node 5 (Resp-01):








#

