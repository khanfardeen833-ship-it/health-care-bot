from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid
import json
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, API_HOST, API_PORT, ALLOWED_ORIGINS

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="Health Symptom Checker API",
    description="A preliminary health assessment tool for symptom checking",
    version="1.0.0"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class SymptomOption(BaseModel):
    value: str
    text: str
    emergency: bool = False

class Question(BaseModel):
    id: str
    text: str
    options: List[SymptomOption]

class SymptomCategory(BaseModel):
    name: str
    questions: List[Question]

class UserResponse(BaseModel):
    session_id: str
    question_id: str
    answer: str

class AssessmentRequest(BaseModel):
    session_id: str
    symptom_key: str
    responses: Dict[str, str]

class RecommendationResponse(BaseModel):
    recommendations: List[str]
    urgency_level: str
    is_emergency: bool
    follow_up_actions: List[str]

class SessionData(BaseModel):
    session_id: str
    symptom_key: Optional[str] = None
    responses: Dict[str, str] = {}
    created_at: datetime
    completed: bool = False

# In-memory storage (in production, use a proper database)
sessions: Dict[str, SessionData] = {}

# Comprehensive symptom database
SYMPTOM_DATABASE = {
    "chest_pain": SymptomCategory(
        name="Chest Pain",
        questions=[
            Question(
                id="severity",
                text="How would you rate your chest pain?",
                options=[
                    SymptomOption(value="severe", text="Severe - crushing, very intense", emergency=True),
                    SymptomOption(value="moderate", text="Moderate - uncomfortable but manageable"),
                    SymptomOption(value="mild", text="Mild - barely noticeable")
                ]
            ),
            Question(
                id="duration",
                text="How long have you had this pain?",
                options=[
                    SymptomOption(value="sudden", text="Started suddenly", emergency=True),
                    SymptomOption(value="hours", text="A few hours"),
                    SymptomOption(value="days", text="Several days"),
                    SymptomOption(value="weeks", text="Weeks or longer")
                ]
            ),
            Question(
                id="associated",
                text="Are you experiencing any of these symptoms?",
                options=[
                    SymptomOption(value="breathing", text="Difficulty breathing", emergency=True),
                    SymptomOption(value="sweating", text="Sweating or nausea", emergency=True),
                    SymptomOption(value="radiating", text="Pain radiating to arm/jaw", emergency=True),
                    SymptomOption(value="none", text="None of these")
                ]
            )
        ]
    ),
    "headache": SymptomCategory(
        name="Headache",
        questions=[
            Question(
                id="severity",
                text="How severe is your headache?",
                options=[
                    SymptomOption(value="worst_ever", text="Worst headache of my life", emergency=True),
                    SymptomOption(value="severe", text="Severe - interfering with activities"),
                    SymptomOption(value="moderate", text="Moderate - manageable"),
                    SymptomOption(value="mild", text="Mild - barely noticeable")
                ]
            ),
            Question(
                id="onset",
                text="How did the headache start?",
                options=[
                    SymptomOption(value="sudden", text="Sudden onset like a thunderclap", emergency=True),
                    SymptomOption(value="gradual", text="Gradually got worse"),
                    SymptomOption(value="normal", text="Normal headache pattern")
                ]
            ),
            Question(
                id="symptoms",
                text="Do you have any of these symptoms?",
                options=[
                    SymptomOption(value="fever_stiff", text="Fever and stiff neck", emergency=True),
                    SymptomOption(value="vision", text="Vision changes or confusion", emergency=True),
                    SymptomOption(value="nausea", text="Nausea or vomiting"),
                    SymptomOption(value="none", text="None of these")
                ]
            )
        ]
    ),
    "fever": SymptomCategory(
        name="Fever",
        questions=[
            Question(
                id="temperature",
                text="What is your temperature?",
                options=[
                    SymptomOption(value="very_high", text="Over 103°F (39.4°C)", emergency=True),
                    SymptomOption(value="high", text="101-103°F (38.3-39.4°C)"),
                    SymptomOption(value="low", text="100-101°F (37.8-38.3°C)"),
                    SymptomOption(value="unknown", text="Don't know exact temperature")
                ]
            ),
            Question(
                id="duration",
                text="How long have you had fever?",
                options=[
                    SymptomOption(value="long", text="More than 3 days"),
                    SymptomOption(value="medium", text="1-3 days"),
                    SymptomOption(value="new", text="Just started today")
                ]
            ),
            Question(
                id="symptoms",
                text="Are you experiencing any of these?",
                options=[
                    SymptomOption(value="breathing", text="Difficulty breathing", emergency=True),
                    SymptomOption(value="severe_symptoms", text="Severe headache or stiff neck", emergency=True),
                    SymptomOption(value="confusion", text="Confusion or altered consciousness", emergency=True),
                    SymptomOption(value="mild_symptoms", text="Body aches or fatigue"),
                    SymptomOption(value="none", text="Just fever")
                ]
            )
        ]
    ),
    "stomach": SymptomCategory(
        name="Stomach/Abdominal Pain",
        questions=[
            Question(
                id="severity",
                text="How severe is your abdominal pain?",
                options=[
                    SymptomOption(value="severe", text="Severe - doubled over in pain", emergency=True),
                    SymptomOption(value="moderate", text="Moderate - uncomfortable"),
                    SymptomOption(value="mild", text="Mild - manageable")
                ]
            ),
            Question(
                id="location",
                text="Where is the pain located?",
                options=[
                    SymptomOption(value="right_lower", text="Right lower abdomen", emergency=True),
                    SymptomOption(value="upper_right", text="Upper right abdomen"),
                    SymptomOption(value="upper", text="Upper abdomen/stomach"),
                    SymptomOption(value="general", text="General/all over")
                ]
            ),
            Question(
                id="symptoms",
                text="Do you have any of these symptoms?",
                options=[
                    SymptomOption(value="vomiting_fever", text="Vomiting and fever", emergency=True),
                    SymptomOption(value="blood", text="Blood in vomit or stool", emergency=True),
                    SymptomOption(value="rigid", text="Rigid, board-like abdomen", emergency=True),
                    SymptomOption(value="nausea", text="Nausea or diarrhea"),
                    SymptomOption(value="none", text="Just pain")
                ]
            )
        ]
    ),
    "respiratory": SymptomCategory(
        name="Breathing/Respiratory Issues",
        questions=[
            Question(
                id="severity",
                text="How severe is your breathing difficulty?",
                options=[
                    SymptomOption(value="severe", text="Severe - can't speak full sentences", emergency=True),
                    SymptomOption(value="moderate", text="Moderate - short of breath with activity"),
                    SymptomOption(value="mild", text="Mild - slightly winded")
                ]
            ),
            Question(
                id="onset",
                text="When did breathing problems start?",
                options=[
                    SymptomOption(value="sudden", text="Suddenly", emergency=True),
                    SymptomOption(value="hours", text="Over several hours"),
                    SymptomOption(value="days", text="Over several days"),
                    SymptomOption(value="gradual", text="Gradually over weeks")
                ]
            ),
            Question(
                id="associated",
                text="Are you experiencing any of these?",
                options=[
                    SymptomOption(value="chest_pain", text="Chest pain", emergency=True),
                    SymptomOption(value="blue_lips", text="Blue lips or fingernails", emergency=True),
                    SymptomOption(value="cough_blood", text="Coughing up blood", emergency=True),
                    SymptomOption(value="fever", text="Fever"),
                    SymptomOption(value="cough", text="Cough only")
                ]
            )
        ]
    )
}

# Emergency detection function
def detect_emergency(symptom_key: str, responses: Dict[str, str]) -> bool:
    """Detect if any response indicates an emergency situation"""
    if symptom_key not in SYMPTOM_DATABASE:
        return False
    
    symptom = SYMPTOM_DATABASE[symptom_key]
    
    for question in symptom.questions:
        response_value = responses.get(question.id)
        if response_value:
            for option in question.options:
                if option.value == response_value and option.emergency:
                    return True
    return False

# OpenAI-enhanced recommendation generation
async def get_openai_recommendations(symptom_key: str, responses: Dict[str, str]) -> str:
    """Get AI-enhanced recommendations from OpenAI"""
    try:
        # Get symptom information
        symptom = SYMPTOM_DATABASE[symptom_key]
        
        # Create a detailed prompt for OpenAI
        prompt = f"""
        You are a medical AI assistant providing preliminary health guidance. 
        
        IMPORTANT: This is for educational purposes only and should not replace professional medical advice.
        
        Symptom Category: {symptom.name}
        User Responses: {json.dumps(responses, indent=2)}
        
        Based on these responses, provide:
        1. A brief assessment of the situation
        2. Specific recommendations for the user
        3. When to seek medical attention
        4. General self-care tips
        
        Keep the response concise, empathetic, and always emphasize consulting healthcare professionals.
        Format the response in a clear, easy-to-read manner with bullet points.
        """
        
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful medical AI assistant providing preliminary health guidance. Always emphasize that this is not a substitute for professional medical advice."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "Unable to generate AI recommendations at this time. Please consult with a healthcare professional."

# Recommendation generation
def generate_recommendations(symptom_key: str, responses: Dict[str, str]) -> RecommendationResponse:
    """Generate recommendations based on symptom assessment"""
    
    is_emergency = detect_emergency(symptom_key, responses)
    
    if is_emergency:
        return RecommendationResponse(
            recommendations=[
                "🚨 This appears to be a medical emergency",
                "Call 911 immediately or go to the nearest emergency room",
                "Do not drive yourself if symptoms are severe",
                "Have someone accompany you if possible"
            ],
            urgency_level="EMERGENCY",
            is_emergency=True,
            follow_up_actions=[
                "Call 911 now",
                "Go to emergency room",
                "Contact emergency services"
            ]
        )
    
    # Generate specific recommendations based on symptom and responses
    recommendations = []
    follow_up_actions = []
    urgency_level = "LOW"
    
    if symptom_key == "chest_pain":
        severity = responses.get("severity", "")
        duration = responses.get("duration", "")
        
        if severity in ["moderate", "severe"] or duration in ["sudden", "hours"]:
            urgency_level = "HIGH"
            recommendations.extend([
                "⚠️ Chest pain requires immediate medical attention",
                "See a doctor or go to urgent care within 4 hours",
                "Don't ignore persistent chest pain",
                "Avoid physical exertion until evaluated"
            ])
            follow_up_actions.extend([
                "Contact healthcare provider immediately",
                "Go to urgent care if doctor unavailable",
                "Monitor for worsening symptoms"
            ])
        else:
            recommendations.extend([
                "💡 For mild chest pain:",
                "Rest and avoid strenuous activity",
                "Monitor for any changes or worsening",
                "See your doctor if pain persists or worsens"
            ])
            follow_up_actions.append("Schedule appointment with primary care doctor")
    
    elif symptom_key == "headache":
        severity = responses.get("severity", "")
        onset = responses.get("onset", "")
        
        if severity == "severe" or onset == "sudden":
            urgency_level = "HIGH"
            recommendations.extend([
                "⚠️ Severe or sudden headaches need prompt evaluation",
                "Contact your healthcare provider today",
                "Seek immediate care if symptoms worsen",
                "Keep a headache diary for your doctor"
            ])
            follow_up_actions.extend([
                "Call doctor today",
                "Consider urgent care if severe",
                "Track headache patterns"
            ])
        else:
            recommendations.extend([
                "💡 For mild to moderate headaches:",
                "Rest in a quiet, dark room",
                "Stay well hydrated",
                "Apply cold or warm compress to head/neck",
                "Consider appropriate over-the-counter pain relief"
            ])
            follow_up_actions.extend([
                "Try home remedies first",
                "See doctor if headaches become frequent"
            ])
    
    elif symptom_key == "fever":
        temperature = responses.get("temperature", "")
        duration = responses.get("duration", "")
        
        if temperature == "high" or duration == "long":
            urgency_level = "MEDIUM"
            recommendations.extend([
                "⚠️ Persistent or high fever needs medical evaluation",
                "Contact your healthcare provider",
                "Continue monitoring temperature",
                "Stay hydrated and rest"
            ])
            follow_up_actions.extend([
                "Call healthcare provider",
                "Monitor temperature every 4 hours",
                "Seek care if fever increases"
            ])
        else:
            recommendations.extend([
                "💡 For low-grade fever:",
                "Rest and stay well hydrated",
                "Monitor temperature regularly",
                "Use fever-reducing medication if appropriate",
                "See doctor if fever persists over 3 days"
            ])
            follow_up_actions.extend([
                "Rest and hydrate",
                "Monitor for 24-48 hours"
            ])
    
    elif symptom_key == "stomach":
        severity = responses.get("severity", "")
        location = responses.get("location", "")
        
        if severity == "moderate" or location == "upper_right":
            urgency_level = "MEDIUM"
            recommendations.extend([
                "⚠️ Abdominal pain can indicate serious conditions",
                "Contact your healthcare provider",
                "Avoid eating until evaluated",
                "Monitor for fever, vomiting, or worsening pain"
            ])
            follow_up_actions.extend([
                "Call healthcare provider",
                "Consider urgent care if worsening"
            ])
        else:
            recommendations.extend([
                "💡 For mild stomach pain:",
                "Try clear liquids and bland foods (BRAT diet)",
                "Stay hydrated with small, frequent sips",
                "Avoid dairy, spicy, and fatty foods",
                "Rest and monitor symptoms"
            ])
            follow_up_actions.extend([
                "Try dietary modifications",
                "See doctor if pain persists over 24 hours"
            ])
    
    elif symptom_key == "respiratory":
        severity = responses.get("severity", "")
        if severity == "moderate":
            urgency_level = "HIGH"
            recommendations.extend([
                "⚠️ Breathing difficulties require prompt medical attention",
                "Contact your healthcare provider immediately",
                "Consider urgent care or emergency room",
                "Sit upright and try to remain calm"
            ])
            follow_up_actions.extend([
                "Seek immediate medical care",
                "Call healthcare provider now"
            ])
        else:
            recommendations.extend([
                "💡 For mild breathing issues:",
                "Rest and avoid exertion",
                "Use a humidifier if helpful",
                "Monitor for worsening symptoms",
                "See doctor if symptoms persist or worsen"
            ])
    
    # Add general recommendations
    recommendations.extend([
        "",
        "🔄 General advice:",
        "• Monitor your symptoms closely",
        "• Seek medical care if symptoms worsen",
        "• This assessment is for guidance only",
        "• Always trust your instincts about your health"
    ])
    
    if urgency_level == "LOW":
        follow_up_actions.append("Monitor symptoms for 24-48 hours")
    
    return RecommendationResponse(
        recommendations=recommendations,
        urgency_level=urgency_level,
        is_emergency=is_emergency,
        follow_up_actions=follow_up_actions
    )

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Health Symptom Checker API",
        "version": "1.0.0",
        "disclaimer": "This API provides preliminary health guidance only and is not a substitute for professional medical advice."
    }

@app.post("/api/session/create")
async def create_session():
    """Create a new assessment session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = SessionData(
        session_id=session_id,
        created_at=datetime.now()
    )
    return {"session_id": session_id}

@app.get("/api/symptoms")
async def get_symptoms():
    """Get available symptom categories"""
    symptoms = []
    for key, symptom in SYMPTOM_DATABASE.items():
        symptoms.append({
            "key": key,
            "name": symptom.name,
            "description": f"Assessment for {symptom.name.lower()}"
        })
    return {"symptoms": symptoms}

@app.get("/api/symptoms/{symptom_key}")
async def get_symptom_questions(symptom_key: str):
    """Get questions for a specific symptom"""
    if symptom_key not in SYMPTOM_DATABASE:
        raise HTTPException(status_code=404, detail="Symptom category not found")
    
    symptom = SYMPTOM_DATABASE[symptom_key]
    return {
        "symptom_key": symptom_key,
        "name": symptom.name,
        "questions": [
            {
                "id": q.id,
                "text": q.text,
                "options": [
                    {
                        "value": opt.value,
                        "text": opt.text,
                        "emergency": opt.emergency
                    }
                    for opt in q.options
                ]
            }
            for q in symptom.questions
        ]
    }

@app.post("/api/assessment/answer")
async def submit_answer(response: UserResponse):
    """Submit an answer to a question"""
    if response.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[response.session_id]
    session.responses[response.question_id] = response.answer
    
    return {
        "session_id": response.session_id,
        "responses_count": len(session.responses),
        "message": "Answer recorded successfully"
    }

@app.post("/api/assessment/complete")
async def complete_assessment(request: AssessmentRequest):
    """Complete assessment and get recommendations"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if request.symptom_key not in SYMPTOM_DATABASE:
        raise HTTPException(status_code=404, detail="Symptom category not found")
    
    # Update session
    session = sessions[request.session_id]
    session.symptom_key = request.symptom_key
    session.responses.update(request.responses)
    session.completed = True
    
    # Generate base recommendations
    recommendations = generate_recommendations(request.symptom_key, request.responses)
    
    # Get AI-enhanced recommendations
    ai_recommendations = await get_openai_recommendations(request.symptom_key, request.responses)
    
    # Add AI recommendations to the response
    recommendations_dict = recommendations.model_dump()
    recommendations_dict["ai_insights"] = ai_recommendations
    
    return {
        "session_id": request.session_id,
        "assessment_complete": True,
        "recommendations": recommendations_dict
    }

@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "symptom_key": session.symptom_key,
        "responses": session.responses,
        "created_at": session.created_at.isoformat(),
        "completed": session.completed
    }

@app.post("/api/analyze-description")
async def analyze_symptom_description(request: dict):
    """Analyze free-form symptom description using AI"""
    try:
        session_id = request.get("session_id")
        description = request.get("description", "")
        
        if not session_id or session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if not description.strip():
            raise HTTPException(status_code=400, detail="No description provided")
        
        # Use AI to analyze the description and suggest symptom category
        ai_analysis = await analyze_symptom_with_ai(description)
        
        return {
            "session_id": session_id,
            "description": description,
            "ai_analysis": ai_analysis,
            "symptom_key": ai_analysis.get("suggested_category"),
            "confidence": ai_analysis.get("confidence", 0.0)
        }
        
    except Exception as e:
        print(f"Error analyzing description: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze description")

async def analyze_symptom_with_ai(description: str) -> dict:
    """Use AI to analyze symptom description and suggest category"""
    try:
        prompt = f"""
        You are a medical AI assistant. Analyze this symptom description and suggest the most appropriate category from these options:
        
        Available categories:
        - chest_pain: Chest Pain (includes heart, chest, breastbone, sternum pain)
        - headache: Headache (includes head pain, migraine, brain pain, skull pain, head pressure)
        - fever: Fever (includes high temperature, hot, burning up, elevated temperature)
        - stomach: Stomach/Abdominal Pain (includes nausea, vomiting, stomach ache, belly pain, digestive issues)
        - respiratory: Breathing/Respiratory Issues (includes shortness of breath, cough, breathing problems, lung issues)
        
        Symptom description: "{description}"
        
        IMPORTANT: Be flexible with language. Consider:
        - Misspellings and typos (e.g., "naushea" = nausea)
        - Informal language (e.g., "brain hurt" = headache)
        - Location descriptions (e.g., "located at brain" = headache)
        - Severity indicators (e.g., "severe" = high severity)
        
        Respond with a JSON object containing:
        {{
            "suggested_category": "category_key",
            "confidence": 0.0-1.0,
            "reasoning": "brief explanation of why this category was chosen",
            "keywords_found": ["list", "of", "relevant", "keywords"],
            "interpreted_description": "cleaned up version of the description"
        }}
        
        If the description doesn't clearly fit any category, set suggested_category to null.
        """
        
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a medical AI assistant. You MUST respond with ONLY valid JSON. No additional text or explanation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.1
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"AI Response: {ai_response}")  # Debug log
        
        # Try to parse JSON response
        try:
            import json
            # Clean up the response - remove any markdown formatting
            if ai_response.startswith("```json"):
                ai_response = ai_response.replace("```json", "").replace("```", "").strip()
            elif ai_response.startswith("```"):
                ai_response = ai_response.replace("```", "").strip()
            
            parsed_response = json.loads(ai_response)
            return parsed_response
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Raw AI Response: {ai_response}")
            
            # Fallback: try to extract category from text
            ai_lower = ai_response.lower()
            if any(word in ai_lower for word in ["stomach", "nausea", "vomit", "belly", "abdominal"]):
                return {
                    "suggested_category": "stomach",
                    "confidence": 0.7,
                    "reasoning": "Detected stomach-related symptoms from text analysis",
                    "keywords_found": ["stomach", "nausea"],
                    "interpreted_description": description
                }
            elif any(word in ai_lower for word in ["head", "headache", "brain", "skull", "migraine"]):
                return {
                    "suggested_category": "headache",
                    "confidence": 0.7,
                    "reasoning": "Detected headache-related symptoms from text analysis",
                    "keywords_found": ["head", "headache"],
                    "interpreted_description": description
                }
            elif any(word in ai_lower for word in ["chest", "heart", "breastbone"]):
                return {
                    "suggested_category": "chest_pain",
                    "confidence": 0.7,
                    "reasoning": "Detected chest-related symptoms from text analysis",
                    "keywords_found": ["chest", "heart"],
                    "interpreted_description": description
                }
            elif any(word in ai_lower for word in ["breath", "cough", "respiratory", "lung"]):
                return {
                    "suggested_category": "respiratory",
                    "confidence": 0.7,
                    "reasoning": "Detected respiratory symptoms from text analysis",
                    "keywords_found": ["breath", "cough"],
                    "interpreted_description": description
                }
            elif any(word in ai_lower for word in ["fever", "temperature", "hot", "burning"]):
                return {
                    "suggested_category": "fever",
                    "confidence": 0.7,
                    "reasoning": "Detected fever-related symptoms from text analysis",
                    "keywords_found": ["fever", "temperature"],
                    "interpreted_description": description
                }
            else:
                return {
                    "suggested_category": None,
                    "confidence": 0.0,
                    "reasoning": f"Unable to parse AI response: {str(e)}",
                    "keywords_found": [],
                    "interpreted_description": description
                }
        
    except Exception as e:
        print(f"AI analysis error: {e}")
        return {
            "suggested_category": None,
            "confidence": 0.0,
            "reasoning": f"AI analysis failed: {str(e)}",
            "keywords_found": []
        }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Health Symptom Checker API...")
    print("🤖 OpenAI Integration: Enabled")
    print(f"📊 API Documentation: http://{API_HOST}:{API_PORT}/docs")
    print(f"🩺 Health Check: http://{API_HOST}:{API_PORT}/api/health")
    print("⚠️  Remember: This is for educational purposes only!")
    uvicorn.run(app, host=API_HOST, port=API_PORT)
