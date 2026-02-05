from pymongo import MongoClient
import datetime

# 1. Connect to MongoDB
uri = "mongodb+srv://qnrhd99_db_user:wj7JZUImwedq0x0E@teama.k58xklb.mongodb.net/"
client = MongoClient(uri)
db = client["UCSI_DB"]
collection = db["Feedback"]

# 2. Insert 'Marker' Data
marker_data = {
    "query": "몽고DB연결확인",
    "response": "축하합니다! 이 답변은 MongoDB 클라우드에서 실시간으로 가져온 데이터입니다.",
    "score": 1,
    "timestamp": datetime.datetime.now(),
    "type": "verification_test"
}

try:
    result = collection.insert_one(marker_data)
    print("✅ 테스트 데이터 주입 성공!")
    print(f"ID: {result.inserted_id}")
    print("이제 챗봇에게 '몽고DB연결확인' 이라고 질문해 보세요.")
except Exception as e:
    print(f"❌ 데이터 주입 실패: {e}")
