from flask import Flask, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# MongoDB connection string - default to localhost if not provided
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://qnrhd99_db_user:wj7JZUImwedq0x0E@teama.k58xklb.mongodb.net/")
DB_NAME = os.getenv("DB_NAME", "UCSI_DB")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

@app.route('/')
def index():
    return jsonify({"message": "Flask MongoDB Test Server is running!"})

@app.route('/test-db')
def test_db():
    try:
        # Check connection
        client.admin.command('ping')
        return jsonify({
            "status": "success",
            "message": "Connected to MongoDB Atlas!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/feedback/add')
def add_feedback():
    try:
        # Sample feedback data
        new_feedback = {
            "name": "Guest",
            "content": "This is a test feedback",
            "rating": 5
        }
        result = db.Feedback.insert_one(new_feedback)
        return jsonify({
            "status": "success",
            "message": "Feedback added!",
            "inserted_id": str(result.inserted_id)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/feedback')
def get_feedback():
    try:
        # Retrieve all feedbacks
        feedbacks = list(db.Feedback.find({}, {"_id": 0}))
        return jsonify({
            "status": "success",
            "count": len(feedbacks),
            "data": feedbacks
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
