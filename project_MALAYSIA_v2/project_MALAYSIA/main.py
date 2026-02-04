"""
University Chatbot API - Main Server
Features:
- AI-powered chatbot with local Ollama LLM
- Student verification by Student Number + Name
- RAG (Retrieval-Augmented Generation) for data queries
- Intent detection by AI
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from data_engine import DataEngine
from ai_engine import AIEngine
import uvicorn
import os
import re
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("UniversityChatbot")

# Initialize App
app = FastAPI(title="University Chatbot API")

# Log Anonymization Middleware
def anonymize_log(data: str) -> str:
    data = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_REDACTED]', data)
    data = re.sub(r'\d{3}-\d{3}-\d{4}', '[PHONE_REDACTED]', data)
    return data

@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    decoded_body = body.decode("utf-8") if body else ""
    safe_body = anonymize_log(decoded_body)
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
DATA_FILE = "Chatbot_TestData.xlsx"
data_engine = DataEngine(DATA_FILE)

MODEL_NAME = "llama3.1:latest"
ai_engine = AIEngine(MODEL_NAME)

# In-memory session storage (for demo - use Redis/DB in production)
verified_sessions = {}

# Request Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class VerifyRequest(BaseModel):
    student_number: str
    name: str
    session_id: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Intent classification is now handled by AIEngine.classify_intent()
# No more hardcoded pattern matching!

# Endpoints

@app.get("/")
def home():
    return RedirectResponse(url="/site/code_hompage.html")

@app.get("/api/health")
def health():
    return {"status": "healthy", "model": MODEL_NAME}

@app.get("/api/stats")
def stats():
    """Public endpoint - general statistics only"""
    return data_engine.get_summary_stats()

@app.post("/api/verify")
async def verify_student(request: VerifyRequest):
    """
    Verify a student by student number and name
    Returns success if the student exists in the database
    """
    student = data_engine.verify_student(request.student_number, request.name)
    
    if student:
        # Store verified session
        verified_sessions[request.session_id] = {
            "student_number": request.student_number,
            "name": request.name,
            "student_data": student
        }
        return {
            "success": True,
            "message": f"Welcome, {request.name}!",
            "student_number": request.student_number
        }
    else:
        return {
            "success": False,
            "message": "Student not found. Please check your student number and name."
        }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Main chat endpoint with LLM-based intent detection and privacy protection
    
    Privacy Rules:
    1. STUDENT_SEARCH and PERSONAL_DATA require login
    2. After login, users can ONLY access their OWN information
    3. Attempting to access another student's data is denied
    """
    user_message = request.message
    session_id = request.session_id
    context = ""
    
    # Check if user is verified
    verified_student = verified_sessions.get(session_id) if session_id else None
    
    # Use AI to classify intent
    intent_result = ai_engine.classify_intent(user_message)
    intent = intent_result.get("intent", "GENERAL")
    search_term = intent_result.get("search_term")
    
    logger.info(f"Intent classified: {intent}, search_term: {search_term}")
    
    # ===========================================
    # PERSONAL_DATA: Requires authentication
    # ===========================================
    
    if intent == "PERSONAL_DATA":
        # Check if user is logged in
        if not verified_student:
            # Friendly message instead of forcing login
            return {
                "response": "🔒 This is student personal information. To view details, please login using the Login button above.",
                "type": "login_hint",
                "user": "guest"
            }
        
        # User is logged in - check if asking about themselves or someone else
        if search_term:
            # Asking about a specific student by name
            logged_in_name = verified_student.get("name", "").lower().strip()
            searched_name = search_term.lower().strip()
            
            # Check if searching for themselves
            is_self_search = (
                searched_name in logged_in_name or 
                logged_in_name in searched_name or
                any(part in logged_in_name for part in searched_name.split())
            )
            
            if is_self_search:
                student_data = verified_student.get("student_data", {})
                context = f"YOUR PERSONAL DATA:\n{student_data}\n\nThis is your information."
            else:
                # Trying to access someone else's data
                return {
                    "response": f"🔒 Privacy Protection: You can only access your own information. You are logged in as '{verified_student['name']}', so you cannot view information about '{search_term}'.",
                    "type": "message",
                    "user": verified_student["name"]
                }
        else:
            # Asking about their own data (my grades, my info, etc.)
            student_data = verified_student.get("student_data", {})
            context = f"STUDENT'S PERSONAL DATA:\n{student_data}\n\nThis is {verified_student['name']}'s information."
    
    # ===========================================
    # GENERAL: Public information (no auth needed)
    # ===========================================
    
    elif intent == "GENERAL":
        # Check if asking for statistics
        message_lower = user_message.lower()
        if any(kw in message_lower for kw in ["how many", "total student", "gender", "ratio", "nationality", "statistics", "student count"]):
            stats = data_engine.get_summary_stats()
            context = f"UNIVERSITY STATISTICS:\n{stats}"
        # Otherwise, just general conversation - no special context
    
    # Generate response
    response = ai_engine.get_response(user_message, data_context=context)
    
    return {
        "response": response,
        "user": verified_student["name"] if verified_student else "guest",
        "type": "message"
    }

@app.post("/api/logout")
async def logout(request: dict):
    """Clear verified session"""
    session_id = request.get("session_id")
    if session_id and session_id in verified_sessions:
        del verified_sessions[session_id]
    return {"success": True}

# Mount Static Files
if os.path.exists("UI_hompage"):
    app.mount("/site", StaticFiles(directory="UI_hompage", html=True), name="site")

if __name__ == "__main__":
    print(f"Starting server with Ollama model: {MODEL_NAME}")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
