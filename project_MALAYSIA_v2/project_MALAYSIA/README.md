# 📋 UCSI University Chatbot - 프로젝트 인수인계서

## 📌 프로젝트 개요

**프로젝트명**: UCSI University AI Chatbot  
**목적**: 대학교 학생들이 개인 정보를 안전하게 조회할 수 있는 AI 챗봇  
**버전**: 2.0.0  
**최종 업데이트**: 2026-02-04

### 주요 특징:
- 🤖 로컬 LLM (Ollama)을 사용한 무료 AI 응답
- 🧠 LLM 기반 의도 분류 (Intent Classification)
- 🔐 개인정보 보호 (본인 정보만 접근 가능)
- 👤 Student Number + Name 기반 인증
- 🎨 깔끔한 UI/UX (Tailwind CSS)

---

## 🛠️ 기술 스택 (Tech Stack)

### Backend
| 기술 | 버전 | 용도 |
|------|------|------|
| **Python** | 3.10+ | 메인 프로그래밍 언어 |
| **FastAPI** | 0.100+ | REST API 웹 프레임워크 |
| **Uvicorn** | 0.22+ | ASGI 서버 |
| **Pandas** | 2.0+ | Excel 데이터 처리 |
| **Openpyxl** | 3.1+ | .xlsx 파일 읽기 |

### AI/LLM
| 기술 | 버전 | 용도 |
|------|------|------|
| **Ollama** | 최신 | 로컬 LLM 실행 엔진 |
| **llama3.1:latest** | 8B | AI 모델 (권장) |

### Frontend
| 기술 | 용도 |
|------|------|
| **HTML5** | 페이지 구조 |
| **Tailwind CSS** | 스타일링 (CDN) |
| **JavaScript (Vanilla)** | 클라이언트 로직 |
| **Material Icons** | 아이콘 (CDN) |

### 인증/보안
| 기술 | 용도 |
|------|------|
| **Session-based Auth** | 세션 기반 인증 |
| **Student Number + Name** | 본인 확인 |

---

## 📁 파일 구조

```
project_MALAYSIA/
├── main.py                 # 🚀 메인 서버 (FastAPI)
├── ai_engine.py            # 🤖 AI 엔진 (Ollama 연결, 의도분류)
├── data_engine.py          # 📊 데이터 엔진 (Excel 처리)
├── auth_utils.py           # 🔐 인증 유틸리티
├── requirements.txt        # 📦 Python 의존성
├── start_chatbot.bat       # ▶️ 실행 스크립트 (Windows)
├── .gitignore              # Git 제외 파일
│
├── Chatbot_TestData.xlsx   # 📋 학생 데이터 (Excel)
├── chatbot_chracter.png    # 🖼️ 챗봇 캐릭터 이미지
│
├── UI_hompage/
│   └── code_hompage.html   # 🌐 메인 웹 페이지
│
├── README.md               # 📖 이 문서
├── Project_SPEC.md         # 📝 프로젝트 명세
├── QA_Report.md            # ✅ QA 리포트
└── project_plan.pdf        # 📄 원본 기획서
```

---

## ⚙️ 환경 설정 가이드

### 1단계: Python 설치
```bash
# Python 3.10 이상 필요
python --version
```
- 다운로드: https://www.python.org/downloads/

### 2단계: Python 의존성 설치
```bash
cd project_MALAYSIA
pip install -r requirements.txt
```

### 3단계: Ollama 설치 (로컬 LLM)
1. **다운로드**: https://ollama.com/download/windows
2. **설치 파일 실행**: OllamaSetup.exe
3. **모델 다운로드** (터미널에서):
```bash
# 권장 모델
ollama pull llama3.1:latest
```

### 4단계: Ollama 실행 확인
```bash
ollama list
```
모델이 목록에 있으면 성공!

---

## 🚀 실행 방법

### 방법 1: 배치 파일 (권장)
```
start_chatbot.bat 더블클릭
```

### 방법 2: 터미널
```bash
cd project_MALAYSIA
python main.py
```

**성공 시 출력:**
```
Data Loaded. Columns: ['Student ID', 'Name', ...]
Ollama connected. Available models: ['llama3.1:latest']
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 브라우저 접속
```
http://localhost:8000
```

---

## 🤖 AI 의도 분류 시스템

### 단순화된 2가지 의도

| 의도 | 설명 | 인증 필요 | 예시 |
|------|------|----------|------|
| **GENERAL** | 일반 정보 (통계 포함) | ❌ 불필요 | "Hello", "How many students?", "Gender ratio?" |
| **PERSONAL_DATA** | 학생 개인 정보 | ✅ 필요 | "Who is Vicky?", "My grades", "Tell me my info" |

### 통계 질문 처리
- "How many students?" → **GENERAL** → 바로 응답
- "What is the gender ratio?" → **GENERAL** → 바로 응답

### 개인정보 질문 처리
- "Who is Vicky?" → **PERSONAL_DATA** → 로그인 안내

---

## 🔐 인증 및 보안 로직

### 로그인 방법
1. 챗봇 헤더의 **Login 버튼** 클릭
2. Student Number + Full Name 입력
3. ✅ 인증 성공 시 버튼이 사용자 이름으로 변경

### 개인정보 보호 규칙

| 시나리오 | 결과 |
|----------|------|
| 미로그인 + "Who is Vicky?" | 🔒 "로그인하세요" 안내 |
| Ryan 로그인 + "Who is Vicky?" | 🔒 접근 거부 (본인 아님) |
| Vicky 로그인 + "Who is Vicky?" | ✅ 정보 제공 |
| Vicky 로그인 + "Show me my info" | ✅ 정보 제공 |

---

## 📊 데이터 파일 (Excel)

### 파일: `Chatbot_TestData.xlsx`
- **중요**: 암호화/보호 해제 필요
- Excel에서 열어서 "다른 이름으로 저장" → 암호 없이 저장

### 컬럼 예시:
- Student Number/ID
- Name
- Gender
- Nationality
- Programme
- Intake
- Status

---

## 🎨 UI 기능

### 챗봇 헤더
- **UCSI Assistant** 제목
- **Online** 상태 표시
- **Login/사용자명** 버튼 (클릭하여 로그인/로그아웃)

### 채팅 화면
- 줄바꿈 지원 (`white-space: pre-line`)
- 이모지 지원 (📋, 📊, 🔒 등)
- 깔끔한 정보 카드 형식

---

## ❗ 트러블슈팅

### Ollama 연결 안됨
```
Warning: Ollama server not running.
```
**해결**: 
- Windows 시작 메뉴에서 "Ollama" 실행
- 또는 터미널에서 `ollama serve`

### Excel 로딩 에러
```
Error loading Excel: Can't find workbook
```
**해결**: Excel 파일 암호 해제 후 다시 저장

### 포트 사용 중
```
Address already in use
```
**해결**: 기존 서버 종료 또는 다른 포트 사용
```bash
uvicorn main:app --port 8001
```

---

## 📝 테스트 시나리오

### 1. 일반 대화 (인증 불필요)
```
입력: "Hello, who are you?"
결과: AI 자기소개 ✅
```

### 2. 통계 조회 (인증 불필요)
```
입력: "How many students are enrolled?"
결과: 📊 통계 정보 표시 ✅
```

### 3. 미로그인 상태에서 개인정보 요청
```
입력: "Who is Vicky Yiran?"
결과: 🔒 "This is student personal information. Please login..." ✅
```

### 4. 로그인 후 본인 정보 조회
```
입력: "Show me my information"
결과: 📋 본인 정보 깔끔하게 표시 ✅
```

### 5. 타인 정보 접근 시도
```
(A로 로그인한 상태)
입력: "Who is B?"
결과: 🔒 "Privacy Protection: You can only access your own information." ✅
```

---

## 📞 Quick Reference

### 필수 명령어
```bash
# 의존성 설치
pip install -r requirements.txt

# Ollama 모델 다운로드
ollama pull llama3.1:latest

# 서버 시작
python main.py
```

### 접속 URL
- 메인 페이지: http://localhost:8000
- API Health: http://localhost:8000/api/health
- API Stats: http://localhost:8000/api/stats

---

**마지막 업데이트**: 2026-02-04  
**버전**: 2.0.0
