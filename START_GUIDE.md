# 🚀 AI-NutriCurator 빠른 시작 가이드

## 1단계: 백엔드 서버 실행

### Windows (PowerShell)

```powershell
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 백엔드 서버 실행
cd backend
python app.py
```

또는:

```powershell
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Mac/Linux

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 백엔드 서버 실행
cd backend
python app.py
```

**✅ 백엔드 서버가 실행되면 다음 메시지를 확인할 수 있습니다:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**🔍 API 문서 확인:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 2단계: 프론트엔드 실행

프론트엔드는 정적 HTML 파일이므로 여러 방법으로 실행할 수 있습니다.

### 방법 1: VSCode Live Server (추천)

1. VSCode에서 `index.html` 파일 열기
2. 마우스 우클릭 → "Open with Live Server" 클릭
3. 브라우저가 자동으로 열립니다 (보통 http://localhost:5500)

### 방법 2: Python 간단 서버

```bash
# 프로젝트 루트 디렉토리에서 실행
python -m http.server 3000
```

그리고 브라우저에서 http://localhost:3000 접속

### 방법 3: 직접 브라우저로 열기

1. `index.html` 파일을 찾아서
2. 브라우저로 드래그 앤 드롭

⚠️ **주의**: 직접 열 경우 CORS 문제가 발생할 수 있습니다. Live Server나 Python 서버 사용을 권장합니다.

---

## 3단계: 사용해보기

### 1. 프로필 선택
- 화면 상단의 "사용자 프로필 선택" 섹션에서 원하는 프로필 클릭
- 예: "당뇨 + 우유/땅콩 알러지 환자"

### 2. 제품 검색 (선택사항)
- 검색창에 제품명 입력 (예: "김치", "과자")
- Enter 키 또는 검색 버튼 클릭

### 3. 알러지 분석
- 제품 카드의 "알러지 분석" 버튼 클릭
- 분석 결과 모달에서 상세 정보 확인

---

## 🐛 문제 해결

### 백엔드 서버가 시작되지 않을 때

```bash
# 포트가 이미 사용 중인 경우
python -m uvicorn backend.app:app --reload --port 8001

# 또는 실행 중인 프로세스 종료 (Windows)
netstat -ano | findstr :8000
taskkill /PID [PID번호] /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### CORS 에러가 발생할 때

백엔드 서버(`backend/app.py`)에서 CORS 설정이 올바른지 확인:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 "*" 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 프론트엔드가 백엔드와 연결되지 않을 때

`index.html` 파일에서 API 주소 확인:

```javascript
const API_BASE_URL = 'http://localhost:8000';
```

포트 번호가 백엔드 서버와 일치하는지 확인하세요.

---

## 📊 테스트 시나리오

### 시나리오 1: 안전한 제품 찾기
1. 프로필: "당뇨 + 우유/땅콩 알러지 환자" 선택
2. 제품: "설화눈꽃팝김부각스낵" 분석
3. 결과: ✅ 안전 (우유, 땅콩 미포함)

### 시나리오 2: 위험한 제품 경고
1. 프로필: "당뇨 + 우유/땅콩 알러지 환자" 선택
2. 제품: "해태 허니버터칩" 분석
3. 결과: ❌ 위험 (우유 포함)

### 시나리오 3: 대체재 추천 확인
1. 프로필: "고혈압 + 새우 알러지 환자" 선택
2. 제품: "고들빼기김치" 분석
3. 결과: ❌ 위험 (새우 포함) + 대체재 추천 확인

---

## 🎯 다음 단계

- [ ] 실제 제품 데이터베이스 연동
- [ ] AI 모델 통합 (`agent_chat_allergy(완).py` 활용)
- [ ] 사용자 계정 시스템 추가
- [ ] 모바일 반응형 UI 개선
- [ ] 제품 바코드 스캔 기능 추가

---

## 💡 팁

- **개발 중**: 백엔드는 `--reload` 옵션으로 실행하면 코드 변경 시 자동으로 재시작됩니다.
- **프로덕션**: 실제 배포 시에는 Nginx, Gunicorn 등을 사용하세요.
- **디버깅**: 브라우저 개발자 도구(F12)의 Console과 Network 탭을 활용하세요.

---

**🎉 이제 AI-NutriCurator를 사용할 준비가 되었습니다!**
