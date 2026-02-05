"""
Data Engine - Student Data Access Layer
Handles Excel data loading and student verification
"""
import pandas as pd
import os
from datetime import datetime
import openpyxl
from pymongo import MongoClient
import re

class DataEngine:
    def __init__(self, student_data_path="Chatbot_TestData.xlsx", feedback_data_path="feedback.xlsx"):
        self.student_path = student_data_path
        self.feedback_path = feedback_data_path
        self.df = None          # Student Data
        self.feedback_df = None # Feedback Data
        
        # MongoDB Setup
        self.mongo_client = None
        self.mongo_db = None
        self.collection = None
        self._connect_mongo()
        
        self.load_data()

    def _connect_mongo(self):
        """Try to connect to MongoDB Atlas"""
        try:
            # URI from team's app.py
            uri = "mongodb+srv://qnrhd99_db_user:wj7JZUImwedq0x0E@teama.k58xklb.mongodb.net/"
            self.mongo_client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            
            # Quick Check
            self.mongo_client.admin.command('ping')
            
            self.mongo_db = self.mongo_client["UCSI_DB"]
            self.collection = self.mongo_db["Feedback"]
            print("✅ Connected to MongoDB Atlas!")
            
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            print("➡️ System will run in Local Excel Mode.")
            self.mongo_client = None
            self.collection = None

    def load_data(self):
        # 1. Load Student Data (Read Only)
        if os.path.exists(self.student_path):
            try:
                self.df = pd.read_excel(self.student_path)
                print(f"Student Data Loaded. Columns: {self.df.columns.tolist()}")
                self.df.columns = [str(c).strip() for c in self.df.columns]
            except Exception as e:
                print(f"Error loading Student Data: {e}")
                self.df = pd.DataFrame()
        else:
            print(f"Student Data file not found: {self.student_path}")
            self.df = pd.DataFrame()
            
        # 2. Load Feedback Data (Local Backup)
        if os.path.exists(self.feedback_path):
            try:
                self.feedback_df = pd.read_excel(self.feedback_path)
                print(f"Local Feedback Data Loaded. Rows: {len(self.feedback_df)}")
            except Exception as e:
                print(f"Error loading Local Feedback: {e}. Creating new.")
                self.feedback_df = pd.DataFrame(columns=["User_Query", "AI_Response", "Score", "Date"])
        else:
            self.feedback_df = pd.DataFrame(columns=["User_Query", "AI_Response", "Score", "Date"])
            try:
                self.feedback_df.to_excel(self.feedback_path, index=False)
            except Exception as e:
                print(f"Error creating feedback file: {e}")

    # ... (get_column_names, verify_student, get_student_info, get_summary_stats, search_students are unchanged) ...

    def get_column_names(self):
        """Return available column names"""
        if self.df is None or self.df.empty:
            return []
        return self.df.columns.tolist()

    def verify_student(self, student_number, name):
        """Verify a student exists with matching student number and name"""
        if self.df is None or self.df.empty:
            return None
        # ... existing logic ...
        # (This part is long, omitting for brevity in replacement but it must be kept)
        # Using a trick to keep existing methods by just replacing the top part and save_feedback part
        # Actually I need to be careful not to delete methods.
        # Let's use the provided tool capability to replace the class definition and specific methods.
        
        # Re-implementing verify_student fully to be safe with replace_file_content
        cols = [c.lower() for c in self.df.columns]
        student_num_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'student' in col_lower and ('number' in col_lower or 'no' in col_lower or 'id' in col_lower):
                student_num_col = col; break
            if col_lower in ['studentno', 'student_no', 'student_id', 'studentid', 'id']:
                student_num_col = col; break
        
        name_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'name' in col_lower and 'nick' not in col_lower:
                name_col = col; break
        
        if not student_num_col or not name_col:
            if len(self.df.columns) >= 2:
                student_num_col = self.df.columns[0]
                name_col = self.df.columns[1]
            else: return None
            
        mask = (
            (self.df[student_num_col].astype(str).str.strip().str.lower() == str(student_number).strip().lower()) &
            (self.df[name_col].astype(str).str.strip().str.lower() == str(name).strip().lower())
        )
        matches = self.df[mask]
        if len(matches) > 0: return matches.iloc[0].to_dict()
        return None

    def get_student_info(self, student_number):
        if self.df is None or self.df.empty: return None
        student_num_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'student' in col_lower and ('number' in col_lower or 'no' in col_lower or 'id' in col_lower):
                student_num_col = col; break
            if col_lower in ['studentno', 'student_no', 'student_id', 'studentid', 'id']:
                student_num_col = col; break
        if not student_num_col: student_num_col = self.df.columns[0]
        mask = self.df[student_num_col].astype(str).str.strip().str.lower() == str(student_number).strip().lower()
        matches = self.df[mask]
        if len(matches) > 0: return matches.iloc[0].to_dict()
        return None

    def get_summary_stats(self):
        if self.df is None or self.df.empty: return {"error": "No data available"}
        stats = {"total_students": len(self.df), "columns": self.df.columns.tolist()}
        for col in self.df.columns:
            if 'gender' in col.lower(): stats["gender_breakdown"] = self.df[col].value_counts().to_dict(); break
        for col in self.df.columns:
            if 'national' in col.lower(): stats["nationality_breakdown"] = self.df[col].value_counts().to_dict(); break
        return stats

    def search_students(self, query):
        if self.df is None or self.df.empty: return []
        results = self.df[self.df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)]
        return results.head(5).to_dict(orient='records')

    def save_feedback(self, query, response, score):
        """
        Save feedback to MongoDB (Primary) and Excel (Backup)
        *** SECURITY UPDATE: Filters out responses containing potential PII ***
        """
        # 0. Safety Check (Privacy Filter)
        # Block if response contains sensitive keywords or patterns (e.g. grades like 3.8, student IDs)
        sensitive_keywords = ['my id', 'my score', 'grade', 'gpa', '학점', '점수', '학번', '성적']
        
        # Check 1: Sensitive keywords in query (User asking for PII)
        if any(k in query.lower() for k in sensitive_keywords):
            print(f"🔒 Security: Feedback rejected due to sensitive query content: {query}")
            return False

        # Check 2: Numbers in response (Likely specific data like 3.5, 12345678)
        # Regex looks for floating point numbers (X.X) or 5+ digit numbers (Student ID)
        if re.search(r'\d+\.\d+', response) or re.search(r'\d{5,}', response):
            print(f"🔒 Security: Feedback rejected due to potential PII (Numbers) in response.")
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. MongoDB Save
        if self.collection is not None:
            try:
                doc = {
                    "query": query,
                    "response": response,
                    "score": int(score),
                    "timestamp": timestamp,
                    "model": "llama3.1",
                    "type": "rlhf"
                }
                self.collection.insert_one(doc)
                print(f"✅ Feedback saved to MongoDB: Score {score}")
            except Exception as e:
                print(f"❌ MongoDB Error: {e}")
        
        # 2. Local Excel Backup (Always save to file for safety)
        try:
            new_entry = {
                "User_Query": query,
                "AI_Response": response,
                "Score": score,
                "Date": timestamp
            }
            new_row_df = pd.DataFrame([new_entry])
            
            if self.feedback_df.empty:
                 self.feedback_df = new_row_df
            else:
                 self.feedback_df = pd.concat([self.feedback_df, new_row_df], ignore_index=True)
            
            self.feedback_df.to_excel(self.feedback_path, index=False)
            print(f"✅ Feedback saved to Excel Backup")
            return True
        except Exception as e:
            print(f"CRITICAL: Local save failed: {e}")
            return False

    def get_relevant_feedback(self, query):
        """
        Retrieve good/bad examples from MongoDB (Priority) or Local Excel
        """
        query_words = set(query.lower().split())
        if not query_words: return {"good": [], "bad": []}

        good_examples = []
        bad_examples = []

        # --- Strategy A: MongoDB (Fast & Rich) ---
        if self.collection is not None:
            try:
                # Get recent feedback (limit 200 for performance)
                cursor = self.collection.find().sort("timestamp", -1).limit(200)
                
                for doc in cursor:
                    past_query = str(doc.get('query', '')).lower()
                    if not past_query: continue
                    
                    # Similarity Check
                    if query.lower() in past_query or past_query in query.lower():
                        is_similar = True
                    else:
                        past_words = set(past_query.split())
                        if not past_words: continue
                        overlap = len(query_words.intersection(past_words))
                        union = len(query_words.union(past_words))
                        is_similar = (overlap / union) > 0.3 if union > 0 else False
                    
                    if is_similar:
                        resp = doc.get('response')
                        sc = doc.get('score')
                        if sc == 1 and resp not in good_examples: good_examples.append(resp)
                        elif sc == -1 and resp not in bad_examples: bad_examples.append(resp)
                        
                        if len(good_examples) >= 3 and len(bad_examples) >= 3: break
                
                return {"good": good_examples[:3], "bad": bad_examples[:3]}
                
            except Exception as e:
                print(f"MongoDB Read Error: {e}. Falling back to Excel.")
        
        # --- Strategy B: Local Excel (Fallback) ---
        if self.feedback_df is None or self.feedback_df.empty:
            return {"good": [], "bad": []}
            
        for idx, row in self.feedback_df.iterrows():
            past_query = str(row['User_Query']).lower()
            past_words = set(past_query.split())
            if not past_words: continue

            if query.lower() in past_query or past_query in query.lower():
                is_similar = True
            else:
                overlap = len(query_words.intersection(past_words))
                union = len(query_words.union(past_words))
                is_similar = (overlap / union) > 0.3 if union > 0 else False
                
            if is_similar:
                resp = str(row['AI_Response'])
                if row['Score'] == 1 and resp not in good_examples: good_examples.append(resp)
                elif row['Score'] == -1 and resp not in bad_examples: bad_examples.append(resp)

        return {"good": good_examples[-3:], "bad": bad_examples[-3:]}


if __name__ == "__main__":
    engine = DataEngine("Chatbot_TestData.xlsx")
    print("\n=== Summary Stats ===")
    print(engine.get_summary_stats())
    print("\n=== Columns ===")
    print(engine.get_column_names())
