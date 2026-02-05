from data_engine import DataEngine
import pandas as pd

try:
    # 엑셀 파일 로드 (Feedback_Log 시트)
    df = pd.read_excel("Chatbot_TestData.xlsx", sheet_name="Feedback_Log")
    
    if df.empty:
        print("피드백 기록이 없습니다.")
    else:
        print(f"총 {len(df)}개의 피드백이 있습니다.\n")
        print("=== 최근 피드백 목록 ===")
        # 최근 5개 출력
        print(df.tail(5)[['Date', 'User_Query', 'Score', 'AI_Response']].to_string())

except ValueError:
    print("아직 'Feedback_Log' 시트가 생성되지 않았습니다. (피드백을 남긴 적이 없음)")
except FileNotFoundError:
    print("Chatbot_TestData.xlsx 파일을 찾을 수 없습니다.")
except Exception as e:
    print(f"오류 발생: {e}")
