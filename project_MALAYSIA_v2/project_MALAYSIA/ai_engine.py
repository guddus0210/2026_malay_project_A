"""
AI Engine - Ollama Local LLM Version with Intent Classification
Connects to local Ollama server for LLM inference
"""
import requests
import json

class AIEngine:
    def __init__(self, model_name="llama3.1:latest"):
        """
        Initialize with Ollama local model
        """
        self.model_name = model_name
        self.base_url = "http://localhost:11434"
        self.chat_history = []
        
        # System prompt context
        self.system_prompt = """You are a helpful and friendly chatbot for UCSI University.
You assist students and visitors with information about the university.
You have access to student data when provided in the context.

RESPONSE STYLE:
- Be concise and friendly
- Use emojis sparingly for visual appeal
- Format data in a clean, readable way

FORMATTING RULES:

1. For STUDENT INFORMATION, use this format:

📋 Student Information
━━━━━━━━━━━━━━━━━━━━━━━━
Student Number: [value]
Name: [value]
Nationality: [value]
Gender: [value]
Programme: [value]
Intake: [value]
Status: [value]
━━━━━━━━━━━━━━━━━━━━━━━━

2. For STATISTICS, use this format:

📊 University Statistics
━━━━━━━━━━━━━━━━━━━━━━━━
Total Students: [number]

👥 Gender Distribution:
   Female: [number] ([percentage]%)
   Male: [number] ([percentage]%)

🌍 Top Nationalities:
   1. [country]: [number]
   2. [country]: [number]
━━━━━━━━━━━━━━━━━━━━━━━━

3. For GENERAL questions, just be helpful and concise.

IMPORTANT: Always put each data field on its OWN LINE. Never concatenate multiple fields on one line.

CRITICAL RULES FOR DATA PRIVACY:
1. NEVER INVENT OR HALLUCINATE STUDENT DATA.
2. If the user asks for personal information (like "academic info", "my grades", "who am I") and NO Context Data is provided, you MUST NOT create fake data.
3. Instead, reply: "🔒 Access Restricted: I cannot show personal information because you are not logged in or no data was found. Please login using the button at the top right."
4. ONLY use information explicitly provided in the 'Context Data' section below. If the context is empty, you know NOTHING about specific students."""

        # Check if Ollama is running
        self._check_connection()
    
    def _check_connection(self):
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                print(f"Ollama connected. Available models: {model_names}")
        except requests.exceptions.ConnectionError:
            print("Warning: Ollama server not running.")
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")

    def classify_intent(self, user_message: str) -> dict:
        """
        Use LLM to classify the intent of the user's message.
        Returns a dict with 'intent' and optionally 'search_term'.
        
        Simplified Intents:
        - GENERAL: Everything that doesn't require authentication (greetings, university info, statistics)
        - PERSONAL_DATA: Anything related to student personal information (my info, who is X, student records)
        """
        classification_prompt = """Classify the following user message into ONE of these intents:

1. GENERAL - General conversation, greetings, university info, programs, statistics (student count, gender ratio, nationality breakdown), campus facilities, etc. Anything that is PUBLIC information.

2. PERSONAL_DATA - Any request for STUDENT PERSONAL information. This includes:
   - User asking about their OWN data ("my grades", "my enrollment", "my info", "show me my details")
   - User asking about a SPECIFIC student by name ("who is John?", "tell me about Mary", "find student X")
   - Any request that would reveal individual student records

If the intent is PERSONAL_DATA and a specific student name is mentioned, extract it as search_term.

Respond in this exact JSON format only, no other text:
{"intent": "INTENT_NAME", "search_term": "student name if mentioned or null"}

User message: """ + user_message

        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": classification_prompt}],
                "stream": False,
                "format": "json"
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("message", {}).get("content", "{}")
                try:
                    parsed = json.loads(content)
                    return parsed
                except json.JSONDecodeError:
                    # Fallback: try to extract intent from text
                    content_upper = content.upper()
                    if "PERSONAL" in content_upper or "STUDENT" in content_upper:
                        return {"intent": "PERSONAL_DATA", "search_term": None}
                    return {"intent": "GENERAL", "search_term": None}
            
            return {"intent": "GENERAL", "search_term": None}
            
        except Exception as e:
            print(f"Intent classification error: {e}")
            return {"intent": "GENERAL", "search_term": None}

    def get_response(self, user_message, data_context="", feedback_context=None):
        """
        Get a response from the local LLM
        """
        try:
            # Build the prompt with context
            prompt_parts = []
            
            if data_context:
                prompt_parts.append(f"Context Data:\n{data_context}")
            
            # RLHF Lite: Add Feedback Context
            if feedback_context:
                if feedback_context.get('good'):
                    good_list = "\n".join([f"- {item}" for item in feedback_context['good']])
                    prompt_parts.append(f"""
Reference (Past Good Answers):
The user previously liked these answers for a similar question. Use them as a style/content guide:
{good_list}
""")
                
                if feedback_context.get('bad'):
                    bad_list = "\n".join([f"- {item}" for item in feedback_context['bad']])
                    prompt_parts.append(f"""
Constraint (Past Bad Answers):
The user previously disliked these answers for a similar question. Do NOT repeat these mistakes:
{bad_list}
""")

            prompt_parts.append(f"User Question: {user_message}")
            
            if data_context:
                prompt_parts.append("Please answer based on the context data provided above. Be specific and use the data.")
            elif feedback_context:
                 prompt_parts.append("Please answer using the feedback references as a guide.")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            # Prepare the request
            payload = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    *self.chat_history[-10:],  # Keep last 10 messages
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False
            }
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result.get("message", {}).get("content", "")
                
                # Update chat history
                self.chat_history.append({"role": "user", "content": user_message})
                self.chat_history.append({"role": "assistant", "content": assistant_message})
                
                return assistant_message
            else:
                return f"Error: Ollama returned status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Cannot connect to Ollama. Make sure Ollama is running."
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Please try a simpler question."
        except Exception as e:
            return f"Error: {str(e)}"

    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []


if __name__ == "__main__":
    print("Testing AI Engine with Intent Classification...")
    engine = AIEngine("llama3.1:latest")
    
    # Test intent classification
    test_messages = [
        "Hello!",
        "How many students are enrolled?",
        "Who is Vicky Yiran?",
        "Tell me about John Smith",
        "What are my grades?",
        "Show me my enrollment status"
    ]
    
    for msg in test_messages:
        intent = engine.classify_intent(msg)
        print(f"Message: '{msg}' -> Intent: {intent}")
