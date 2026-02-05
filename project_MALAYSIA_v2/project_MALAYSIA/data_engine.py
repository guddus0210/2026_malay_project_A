"""
Data Engine - Student Data Access Layer
Handles Excel data loading and student verification
"""
import pandas as pd
import os
from datetime import datetime
import openpyxl

class DataEngine:
    def __init__(self, student_data_path="Chatbot_TestData.xlsx", feedback_data_path="feedback.xlsx"):
        self.student_path = student_data_path
        self.feedback_path = feedback_data_path
        self.df = None          # Student Data
        self.feedback_df = None # Feedback Data
        self.load_data()

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
            
        # 2. Load Feedback Data (Read/Write)
        if os.path.exists(self.feedback_path):
            try:
                self.feedback_df = pd.read_excel(self.feedback_path)
                print(f"Feedback Data Loaded. Rows: {len(self.feedback_df)}")
            except Exception as e:
                print(f"Error loading Feedback Data: {e}. Creating new.")
                self.feedback_df = pd.DataFrame(columns=["User_Query", "AI_Response", "Score", "Date"])
        else:
            print(f"Feedback Log not found. Creating new: {self.feedback_path}")
            self.feedback_df = pd.DataFrame(columns=["User_Query", "AI_Response", "Score", "Date"])
            # Create file immediately to ensure permissions
            try:
                self.feedback_df.to_excel(self.feedback_path, index=False)
            except Exception as e:
                print(f"Error creating feedback file: {e}")

    def get_column_names(self):
        """Return available column names"""
        if self.df is None or self.df.empty:
            return []
        return self.df.columns.tolist()

    def verify_student(self, student_number, name):
        """
        Verify a student exists with matching student number and name
        Returns the student record if found, None otherwise
        """
        if self.df is None or self.df.empty:
            return None
        
        # Find columns that might be student number and name
        cols = [c.lower() for c in self.df.columns]
        
        # Try to find student number column
        student_num_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'student' in col_lower and ('number' in col_lower or 'no' in col_lower or 'id' in col_lower):
                student_num_col = col
                break
            if col_lower in ['studentno', 'student_no', 'student_id', 'studentid', 'id']:
                student_num_col = col
                break
        
        # Try to find name column
        name_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'name' in col_lower and 'nick' not in col_lower:
                name_col = col
                break
        
        if not student_num_col or not name_col:
            print(f"Could not find student number or name columns. Available: {self.df.columns.tolist()}")
            # Fallback: use first two columns
            if len(self.df.columns) >= 2:
                student_num_col = self.df.columns[0]
                name_col = self.df.columns[1]
            else:
                return None
        
        print(f"Using columns: StudentNum='{student_num_col}', Name='{name_col}'")
        
        # Search for matching student
        mask = (
            (self.df[student_num_col].astype(str).str.strip().str.lower() == str(student_number).strip().lower()) &
            (self.df[name_col].astype(str).str.strip().str.lower() == str(name).strip().lower())
        )
        
        matches = self.df[mask]
        
        if len(matches) > 0:
            # Return first match as dict
            student_data = matches.iloc[0].to_dict()
            return student_data
        
        return None

    def get_student_info(self, student_number):
        """Get a specific student's information by student number"""
        if self.df is None or self.df.empty:
            return None
        
        # Find student number column
        student_num_col = None
        for col in self.df.columns:
            col_lower = col.lower()
            if 'student' in col_lower and ('number' in col_lower or 'no' in col_lower or 'id' in col_lower):
                student_num_col = col
                break
            if col_lower in ['studentno', 'student_no', 'student_id', 'studentid', 'id']:
                student_num_col = col
                break
        
        if not student_num_col:
            student_num_col = self.df.columns[0]
        
        mask = self.df[student_num_col].astype(str).str.strip().str.lower() == str(student_number).strip().lower()
        matches = self.df[mask]
        
        if len(matches) > 0:
            return matches.iloc[0].to_dict()
        return None

    def get_summary_stats(self):
        """Get general statistics (non-sensitive)"""
        if self.df is None or self.df.empty:
            return {"error": "No data available"}
        
        stats = {
            "total_students": len(self.df),
            "columns": self.df.columns.tolist()
        }
        
        # Add gender breakdown if available
        for col in self.df.columns:
            if 'gender' in col.lower():
                stats["gender_breakdown"] = self.df[col].value_counts().to_dict()
                break
        
        # Add nationality breakdown if available
        for col in self.df.columns:
            if 'national' in col.lower():
                stats["nationality_breakdown"] = self.df[col].value_counts().to_dict()
                break
        
        return stats

    def search_students(self, query):
        """Search students (limited info for privacy)"""
        if self.df is None or self.df.empty:
            return []
        
        results = self.df[self.df.astype(str).apply(
            lambda x: x.str.contains(query, case=False, na=False)
        ).any(axis=1)]
        
        return results.head(5).to_dict(orient='records')

    def save_feedback(self, query, response, score):
        """
        Save user feedback to 'feedback.xlsx' (Overwrites file safely)
        Score: 1 (Like), -1 (Dislike)
        """
        try:
            new_entry = {
                "User_Query": query,
                "AI_Response": response,
                "Score": score,
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 1. Update in-memory dataframe
            new_row_df = pd.DataFrame([new_entry])
            if self.feedback_df.empty:
                 self.feedback_df = new_row_df
            else:
                 self.feedback_df = pd.concat([self.feedback_df, new_row_df], ignore_index=True)
            
            # 2. Save directly to feedback.xlsx (Full Overwrite)
            # This is the safest way to prevent file corruption
            self.feedback_df.to_excel(self.feedback_path, index=False)
            
            print(f"Feedback saved to {self.feedback_path}: {query[:20]}... Score: {score}")
            return True
            
        except Exception as e:
            print(f"Critical error in save_feedback: {e}")
            return False

    def get_relevant_feedback(self, query):
        """
        Find past feedback (Good & Bad) for similar queries.
        Returns: {"good": [list of strings], "bad": [list of strings]}
        """
        if self.feedback_df is None or self.feedback_df.empty:
            return {"good": [], "bad": []}
        
        query_words = set(query.lower().split())
        good_examples = []
        bad_examples = []
        
        for idx, row in self.feedback_df.iterrows():
            past_query = str(row['User_Query']).lower()
            past_words = set(past_query.split())
            
            # Skip if query is too short
            if len(past_words) == 0: continue

            # Calculate Jaccard similarity (word overlap)
            overlap = len(query_words.intersection(past_words))
            union = len(query_words.union(past_words))
            
            if union == 0: continue
            
            similarity = overlap / union
            
            # Threshold: 30% similarity or check if one contains the other
            is_similar = False
            if similarity > 0.3:
                is_similar = True
            elif query.lower() in past_query or past_query in query.lower():
                # Direct substring match
                is_similar = True
                
            if is_similar:
                response_text = str(row['AI_Response'])
                # Only add if not duplicate
                if row['Score'] == 1:
                    if response_text not in good_examples:
                        good_examples.append(response_text)
                elif row['Score'] == -1:
                     if response_text not in bad_examples:
                        bad_examples.append(response_text)
        
        # Limit to top 3 recent examples to avoid prompt overflow
        return {
            "good": good_examples[-3:], 
            "bad": bad_examples[-3:]
        }


if __name__ == "__main__":
    engine = DataEngine("Chatbot_TestData.xlsx")
    print("\n=== Summary Stats ===")
    print(engine.get_summary_stats())
    print("\n=== Columns ===")
    print(engine.get_column_names())
