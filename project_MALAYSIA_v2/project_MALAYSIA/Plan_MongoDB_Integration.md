# ☁️ MongoDB 기반 적응형 피드백 시스템 통합 계획서

## 1. 개요 (Overview)
**목표**: 로컬 `feedback.xlsx` 파일 대신, 팀원이 구축한 **MongoDB Atlas (클라우드 DB)**를 사용하여 피드백 데이터를 저장하고 검색하도록 시스템을 업그레이드합니다. 이를 통해 데이터의 영속성, 동시성 처리 능력, 검색 속도를 획기적으로 개선합니다.

---

## 2. MongoDB 연결 정보 (Connection Details)
*   **Cluster**: `teama.k58xklb.mongodb.net`
*   **Database**: `UCSI_DB`
*   **Collection**: `Feedback`
*   **Driver**: `pymongo` (Python 공식 드라이버)

---

## 3. 데이터 스키마 (Schema Design)
기존 엑셀 컬럼과 호환되면서, MongoDB의 유연성을 활용하는 JSON 구조로 저장합니다.

```json
{
  "user_query": "등록금 얼마야?",        // (String) 사용자의 질문
  "ai_response": "약 300만원입니다.",    // (String) AI의 답변
  "score": 1,                           // (Int) 1: 좋아요, -1: 싫어요
  "timestamp": "2026-02-05T12:00:00",   // (String or Date) 시간
  "meta": {                             // (Object) 추가 메타데이터 (확장성)
    "source": "chatbot_v2",
    "version": "1.0"
  }
}
```

---

## 4. 구현 로드맵 (Refactoring Roadmap)

### 1단계: 의존성 설치 (Dependencies)
- `pymongo` 라이브러리 추가 필요.
- `requirements.txt` 업데이트.

### 2단계: DataEngine 업그레이드 (Backend Code)
**파일**: `data_engine.py`

1.  **`MongoDataEngine` 클래스 도입 (또는 기존 클래스 확장)**
    -   초기화 시 `MongoClient` 연결.
    -   연결 실패 시 자동으로 기존 `Excel` 모드로 전환하는 **Hybrid Mode** 구현 (안전장치).

2.  **`save_feedback` 메서드 수정**
    -   `db.Feedback.insert_one()` 호출.
    -   비동기 처리는 아니지만, DB 저장이 매우 빠르므로 사용자 경험 저하 없음.

3.  **`get_relevant_feedback` 메서드 수정**
    -   **Good Examples**: `db.Feedback.find({"score": 1}).sort("timestamp", -1).limit(100)`
    -   **Bad Examples**: `db.Feedback.find({"score": -1}).sort("timestamp", -1).limit(100)`
    -   가져온 100개 데이터 중에서 Python 레벨에서 텍스트 유사도(Jaccard/Containment) 계산 수행.
    -   *(추후 고도화: Atlas Vector Search를 사용하면 DB 레벨에서 유사도 검색 가능)*

---

## 5. 단계별 실행 계획 (Action Plan)

1.  **패키지 설치**: `pip install pymongo python-dotenv`
2.  **코드 수정 (`data_engine.py`)**:
    -   DB 연결 코드 추가.
    -   기존 엑셀 저장 코드는 `_save_to_excel`로 백업 메서드화.
    -   메인 로직을 DB 중심으로 변경.
3.  **마이그레이션 (선택)**:
    -   기존 `feedback.xlsx`에 쌓인 데이터가 있다면 MongoDB로 업로드하는 1회성 스크립트 작성.

---

## 6. 테스트 시나리오
1.  서버 실행 시 "Connected to MongoDB" 로그 확인.
2.  질문 -> 좋아요 클릭.
3.  MongoDB Compass 또는 `Mongo_DB/app.py`를 통해 데이터가 들어왔는지 확인.
