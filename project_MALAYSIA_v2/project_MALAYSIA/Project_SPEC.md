# UCSI University Chatbot - 프로젝트 명세서

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | UCSI University AI Chatbot |
| **목적** | 학생 개인정보 보호와 RAG 기반 질의응답 |
| **버전** | 1.0.0 |
| **최종 업데이트** | 2026-02-04 |

---

## 기술 스택

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Data Processing**: Pandas, Openpyxl

### AI/LLM
- **Engine**: Ollama (Local LLM)
- **Model**: llama3.1:latest
- **Features**: Intent Classification, RAG

### Frontend
- **HTML5** + **Tailwind CSS** (CDN)
- **JavaScript** (Vanilla)
- **Icons**: Material Icons (CDN)

### 인증
- **방식**: Session-based (Student Number + Name)
- **보안**: 본인 정보만 접근 가능

---

## 파일 구조

```
project_MALAYSIA/
├── main.py                 # FastAPI 메인 서버
├── ai_engine.py            # AI 엔진 (Ollama 연결, 의도분류)
├── data_engine.py          # 데이터 엔진 (Excel 처리)
├── auth_utils.py           # 인증 유틸리티
├── requirements.txt        # Python 의존성
├── start_chatbot.bat       # 실행 스크립트 (Windows)
├── .gitignore              # Git 제외 파일
│
├── Chatbot_TestData.xlsx   # 학생 데이터
├── chatbot_chracter.png    # 챗봇 캐릭터 이미지
│
├── UI_hompage/
│   └── code_hompage.html   # 메인 웹 UI
│
├── README.md               # 인수인계 문서
├── Project_SPEC.md         # 이 파일
├── project_plan.pdf        # 원본 기획서
│
└── [참고 문서]
    ├── SKILL.md
    ├── plan-template.md
    ├── springboot-vibe-coding-lab.md
    └── QA_Report.md
```

---

## 핵심 기능

### 1. AI 의도 분류 (Intent Classification)
LLM이 사용자 메시지를 분석하여 4가지 의도로 분류:
- `GENERAL`: 일반 대화
- `STATISTICS`: 통계 요청
- `STUDENT_SEARCH`: 특정 학생 검색
- `PERSONAL_DATA`: 본인 정보 요청

### 2. 개인정보 보호
- 학생 검색/개인정보 → 로그인 필수
- 로그인 후에도 **본인 정보만** 접근 가능
- 타인 정보 접근 시도 → 차단

### 3. 통계 조회
- 전체 학생 수, 성별 비율, 국적 분포 등
- 누구나 조회 가능 (집계 데이터)

---

## API 엔드포인트

| Method | Path | 설명 | 인증 |
|--------|------|------|------|
| GET | `/` | 메인 페이지 리다이렉트 | - |
| GET | `/api/health` | 서버 상태 확인 | - |
| GET | `/api/stats` | 통계 조회 | - |
| POST | `/api/verify` | 학생 인증 | - |
| POST | `/api/chat` | 챗봇 대화 | 선택적 |
| POST | `/api/logout` | 로그아웃 | - |

---

## 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. Ollama 설치 및 모델 다운로드
```bash
# https://ollama.com 에서 설치 후
ollama pull llama3.1:latest
```

### 3. 서버 시작
```bash
python main.py
# 또는
start_chatbot.bat (더블클릭)
```

### 4. 브라우저 접속
```
http://localhost:8000
```

---

## 테스트 시나리오

| # | 테스트 | 예상 결과 |
|---|--------|----------|
| 1 | "Hello" 입력 | 일반 인사 응답 |
| 2 | "How many students?" | 통계 정보 표시 |
| 3 | 미로그인 + "Who is Vicky?" | 로그인 요청 |
| 4 | Ryan 로그인 + "Who is Vicky?" | 접근 거부 |
| 5 | Vicky 로그인 + "Tell me my info" | Vicky 정보 표시 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-02-04 | 1.0.0 | 로컬 LLM 전환, 의도분류 추가 |
| 2026-02-04 | 0.9.0 | 개인정보 보호 로직 강화 |
| 2026-02-03 | 0.8.0 | Student Number + Name 인증 |
