# Health Symptom Checker - Backend

A FastAPI-based REST API for health symptom analysis and recommendations with OpenAI integration.

## Features

- **AI-Enhanced Analysis**: Uses OpenAI GPT-3.5-turbo for intelligent symptom assessment
- **Comprehensive Symptom Database**: 5 major symptom categories with detailed questions
- **Emergency Detection**: Automatic detection of emergency situations
- **Session Management**: UUID-based session tracking for user assessments
- **Intelligent Recommendations**: Context-aware recommendations based on symptom severity
- **Real-time API**: FastAPI with automatic documentation and CORS support

## API Endpoints

### Health Check
- `GET /api/health` - Check if the API is running

### Session Management
- `POST /api/session/create` - Create a new assessment session
- `GET /api/session/{session_id}` - Get session information

### Symptoms
- `GET /api/symptoms` - Get all available symptom categories
- `GET /api/symptoms/{symptom_key}` - Get questions for a specific symptom

### Assessment
- `POST /api/assessment/answer` - Submit an answer to a question
- `POST /api/assessment/complete` - Complete assessment and get AI-enhanced recommendations

## Installation

1. **Navigate to backend directory**
   ```bash
   cd health-symptom-checker/backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OpenAI API Key**
   The OpenAI API key is already configured in `config.py`. Make sure you have access to the OpenAI API.

5. **Run the application**
   ```bash
   python start.py
   # OR
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Usage Examples

### Check API Health
```bash
curl http://localhost:8000/api/health
```

### Create Session
```bash
curl -X POST http://localhost:8000/api/session/create
```

### Get Available Symptoms
```bash
curl http://localhost:8000/api/symptoms
```

### Get Symptom Questions
```bash
curl http://localhost:8000/api/symptoms/chest_pain
```

### Complete Assessment
```bash
curl -X POST http://localhost:8000/api/assessment/complete \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "symptom_key": "chest_pain",
    "responses": {
      "severity": "moderate",
      "duration": "hours",
      "associated": "none"
    }
  }'
```

## Configuration

The application uses `config.py` for configuration:

- **OpenAI API Key**: Already configured
- **OpenAI Model**: gpt-3.5-turbo
- **API Host**: 0.0.0.0
- **API Port**: 8000
- **CORS Origins**: localhost:3000, 127.0.0.1:3000

## Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── config.py            # Configuration settings
├── start.py             # Startup script
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## AI Integration

The backend integrates with OpenAI's GPT-3.5-turbo model to provide:

- **Enhanced Recommendations**: AI-generated insights based on user responses
- **Contextual Analysis**: Understanding of symptom patterns and severity
- **Personalized Guidance**: Tailored advice for specific situations
- **Medical Disclaimers**: Always emphasizes consulting healthcare professionals

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Disclaimer

This application is for informational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult with a qualified healthcare provider for medical concerns.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
