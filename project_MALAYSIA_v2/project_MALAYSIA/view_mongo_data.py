from pymongo import MongoClient
import pandas as pd

# Connect
uri = "mongodb+srv://qnrhd99_db_user:wj7JZUImwedq0x0E@teama.k58xklb.mongodb.net/"
client = MongoClient(uri)
db = client["UCSI_DB"]
collection = db["Feedback"]

print(f"\n📊 Connected to: {db.name}")
print(f"📂 Collection: {collection.name}")
print("="*50)

# Get all data
cursor = collection.find().sort("timestamp", -1)
docs = list(cursor)

if not docs:
    print("📭 데이터가 없습니다.")
else:
    print(f"총 {len(docs)}개의 데이터가 발견되었습니다.\n")
    for i, doc in enumerate(docs, 1):
        print(f"[{i}] {doc.get('timestamp', 'No Date')}")
        print(f"   Score: {doc.get('score')}")
        print(f"   Query: {doc.get('query')}")
        print(f"   Response: {doc.get('response')[:50]}...") # 긴 답변은 자름
        print("-" * 30)

print("\n✅ End of Report")
