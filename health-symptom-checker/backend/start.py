#!/usr/bin/env python3
"""
Health Symptom Checker Backend Startup Script
"""

import uvicorn
from config import API_HOST, API_PORT

if __name__ == "__main__":
    print("🚀 Starting Health Symptom Checker API...")
    print("🤖 OpenAI Integration: Enabled")
    print(f"📊 API Documentation: http://{API_HOST}:{API_PORT}/docs")
    print(f"🩺 Health Check: http://{API_HOST}:{API_PORT}/api/health")
    print("⚠️  Remember: This is for educational purposes only!")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
