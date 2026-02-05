# 🧠 적응형 강화학습(RLHF) - 데이터 분리 전략 계획서

## 1. 개요 (Overview)
**목표**: 원본 데이터(`Chatbot_TestData.xlsx`)의 무결성을 보호하기 위해 **읽기 전용(Read-Only)**으로 사용하고, 사용자 피드백 데이터는 **별도의 독립된 파일(`feedback.xlsx`)**에 저장하여 시스템의 안정성과 데이터 안전성을 확보합니다.

---

## 2. 데이터 아키텍처 (Data Architecture)

### 📂 Source A: 학생 데이터 (Master Data)
- **파일**: `Chatbot_TestData.xlsx`
- **모드**: **Read-Only (읽기 전용)**
- **역할**: 학생 정보, 학사 정보 제공. 시스템은 이 파일을 절대 수정하지 않음.

### 📂 Source B: 피드백 로그 (Transaction Data)
- **파일**: `feedback.xlsx` (New!)
- **모드**: **Read/Write (읽기/쓰기)**
- **역할**: 사용자 피드백(좋아요/싫어요) 기록 저장.
- **초기 상태**: 파일이 없으면 시스템이 자동으로 빈 파일을 생성.

---

## 3. 구현 상세 (Implementation)

### `data_engine.py` 변경
1.  **초기화 (`__init__`)**:
    -   `student_data_path`와 `feedback_data_path`를 분리하여 관리.
2.  **데이터 로드 (`load_data`)**:
    -   학생 데이터는 기존대로 로드.
    -   `feedback.xlsx` 존재 여부 확인 후 로드 또는 새 DataFrame 생성.
3.  **피드백 저장 (`save_feedback`)**:
    -   `Chatbot_TestData.xlsx`를 건드리지 않음.
    -   `feedback_df`에 행을 추가하고, `feedback.xlsx`에만 저장.
    -   파일 간 충돌 방지를 위해 `Append` 모드보다는 `Overwrite` (전체 다시 쓰기) 방식 권장 (데이터 양이 적으므로 안전).

### `main.py` 및 `ai_engine.py`
- 기존 로직 유지 (DataEngine 내부 구현만 바뀌므로 수정 불필요).

---

## 4. 기대 효과
1.  **안전성**: 엑셀 파일을 열어놓고 작업해도 피드백 저장이 `feedback.xlsx`에서 따로 일어나므로 충돌 확률 급감.
2.  **보안**: 원본 학생 데이터가 실수로 삭제되거나 변조될 위험 0%.
3.  **확장성**: 추후 `feedback.xlsx`만 MongoDB의 `Logs` 컬렉션으로, `Chatbot_TestData.xlsx`는 `Students` 컬렉션으로 1:1 마이그레이션하기 매우 수월함.
