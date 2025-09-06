import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, AlertTriangle, Phone, Clock, Heart, Activity } from 'lucide-react';
import axios from 'axios';

const HealthSymptomChecker = () => {
  const [currentStep, setCurrentStep] = useState('welcome');
  const [messages, setMessages] = useState([]);
  const [userResponses, setUserResponses] = useState({});
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentSymptom, setCurrentSymptom] = useState(null);
  const [availableSymptoms, setAvailableSymptoms] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [isWaitingForDescription, setIsWaitingForDescription] = useState(false);
  const messagesEndRef = useRef(null);
  
  // API Base URL - use environment variable or fallback to deployed backend
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://health-care-bot-mk9o.onrender.com';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // API Functions
  const apiCall = async (endpoint, method = 'GET', data = null) => {
    try {
      const config = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      };
      
      if (data) {
        config.body = JSON.stringify(data);
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      addMessage("⚠️ Connection error. Please check that the Python backend is running on port 8000.", true);
      throw error;
    }
  };

  const createSession = async () => {
    try {
      const response = await apiCall('/api/session/create', 'POST');
      setSessionId(response.session_id);
      return response.session_id;
    } catch (error) {
      console.error('Failed to create session:', error);
      return null;
    }
  };

  const loadSymptoms = async () => {
    try {
      const response = await apiCall('/api/symptoms');
      setAvailableSymptoms(response.symptoms);
    } catch (error) {
      console.error('Failed to load symptoms:', error);
    }
  };

  const loadSymptomQuestions = async (symptomKey) => {
    try {
      const response = await apiCall(`/api/symptoms/${symptomKey}`);
      return response;
    } catch (error) {
      console.error('Failed to load symptom questions:', error);
      return null;
    }
  };

  const submitAnswer = async (questionId, answer) => {
    try {
      await apiCall('/api/assessment/answer', 'POST', {
        session_id: sessionId,
        question_id: questionId,
        answer: answer
      });
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  const completeAssessment = async (symptomKey, responses) => {
    try {
      const response = await apiCall('/api/assessment/complete', 'POST', {
        session_id: sessionId,
        symptom_key: symptomKey,
        responses: responses
      });
      return response.recommendations;
    } catch (error) {
      console.error('Failed to complete assessment:', error);
      return null;
    }
  };

  const addMessage = (text, isBot = true, options = null, isEmergency = false) => {
    const message = {
      id: Date.now(),
      text,
      isBot,
      options,
      isEmergency,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const addTypingMessage = async (text, delay = 1500) => {
    setIsTyping(true);
    await new Promise(resolve => setTimeout(resolve, delay));
    setIsTyping(false);
    addMessage(text);
  };

  const handleWelcome = async () => {
    // Initialize session
    setIsLoading(true);
    const newSessionId = await createSession();
    if (!newSessionId) {
      addMessage("⚠️ Unable to start session. Please make sure the Python backend is running and refresh the page.", true);
      setIsLoading(false);
      return;
    }
    
    // Load available symptoms
    await loadSymptoms();
    setIsLoading(false);
    
    await addTypingMessage("Hello! I'm your Health Symptom Assistant. 🩺");
    await addTypingMessage("⚠️ IMPORTANT DISCLAIMER: I am NOT a doctor and cannot provide medical diagnoses. This tool is for informational purposes only and should not replace professional medical advice.", 2000);
    await addTypingMessage("🚨 EMERGENCY: If you're experiencing a medical emergency, call 911 immediately or go to your nearest emergency room.");
    await addTypingMessage("By continuing, you understand this is for general guidance only. Do you wish to continue?", 1500);
    
    addMessage("", true, [
      { value: 'continue', text: '✅ Yes, I understand and want to continue' },
      { value: 'emergency', text: '🚨 I need emergency help now' }
    ]);
  };

  const handleEmergencyResponse = () => {
    addMessage("🚨 CALL 911 IMMEDIATELY 🚨", true, null, true);
    addMessage("This appears to be a medical emergency. Please:", true);
    addMessage("• Call 911 or your local emergency number\n• Go to the nearest emergency room\n• If possible, have someone drive you\n• Don't drive yourself if symptoms are severe", true);
    setCurrentStep('complete');
  };

  const handleSymptomSelection = async () => {
    if (availableSymptoms.length === 0) {
      addMessage("⚠️ Unable to load symptom categories. Please make sure the Python backend is running and try again.", true);
      return;
    }
    
    await addTypingMessage("I'll help you assess your symptoms. Let's start with a simple question:");
    await addTypingMessage("What symptoms are you experiencing today? You can describe them in your own words, and I'll guide you through the assessment.");
    
    addMessage("", true, [
      { value: 'describe', text: '💬 I want to describe my symptoms' },
      { value: 'categories', text: '📋 Show me symptom categories' }
    ]);
  };

  const handleSymptomDescription = async () => {
    await addTypingMessage("Perfect! Please describe your symptoms in detail. For example:");
    await addTypingMessage("• What kind of pain or discomfort are you feeling?");
    await addTypingMessage("• Where is it located?");
    await addTypingMessage("• When did it start?");
    await addTypingMessage("• How severe is it?");
    await addTypingMessage("• Are there any other symptoms?");
    
    setIsWaitingForDescription(true);
    addMessage("", true, [
      { value: 'back', text: '⬅️ Go back to options' }
    ]);
  };

  const processSymptomDescription = async (description) => {
    setIsLoading(true);
    setIsWaitingForDescription(false);
    
    try {
      // Send description to backend for AI analysis
      const response = await axios.post(`${API_BASE_URL}/api/analyze-description`, {
        session_id: sessionId,
        description: description
      });
      
      if (response.data.symptom_key) {
        // AI identified a specific symptom category
        const aiAnalysis = response.data.ai_analysis;
        await addTypingMessage("Thank you for describing your symptoms. I understand you're experiencing:");
        
        if (aiAnalysis.interpreted_description) {
          await addTypingMessage(`"${aiAnalysis.interpreted_description}"`);
        }
        
        await addTypingMessage(`Based on your description, I believe this relates to ${aiAnalysis.reasoning || 'your symptoms'}.`);
        await addTypingMessage("Let me guide you through some specific questions to better assess your situation.");
        
        setCurrentStep('assessment');
        setCurrentQuestionIndex(0);
        setUserResponses({});
        await handleQuestionFlow(response.data.symptom_key);
      } else {
        // AI couldn't identify specific category, show general options
        await addTypingMessage("I understand you're experiencing symptoms, but I need a bit more information to help you effectively.");
        await addTypingMessage("Which of these areas best matches your main concern?");
        
        const symptomOptions = availableSymptoms.map(symptom => ({
          value: symptom.key,
          text: symptom.name
        }));
        
        addMessage("", true, [...symptomOptions, { value: 'other', text: 'Something else/Not sure' }]);
      }
    } catch (error) {
      console.error('Error processing description:', error);
      await addTypingMessage("I had trouble processing your description. Let me show you the symptom categories instead.");
      
      const symptomOptions = availableSymptoms.map(symptom => ({
        value: symptom.key,
        text: symptom.name
      }));
      
      addMessage("", true, [...symptomOptions, { value: 'other', text: 'Something else/Not sure' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuestionFlow = async (symptomKey) => {
    if (currentQuestionIndex === 0) {
      // Load symptom questions from API
      const symptomData = await loadSymptomQuestions(symptomKey);
      if (!symptomData) {
        addMessage("⚠️ Unable to load questions. Please try again.", true);
        return;
      }
      setCurrentSymptom(symptomData);
    }

    if (!currentSymptom || currentQuestionIndex >= currentSymptom.questions.length) {
      // All questions answered, complete assessment
      await completeSymptomAssessment(symptomKey);
      return;
    }

    const question = currentSymptom.questions[currentQuestionIndex];
    await addTypingMessage(question.text);
    addMessage("", true, question.options);
  };

  const completeSymptomAssessment = async (symptomKey) => {
    setIsLoading(true);
    
    const recommendations = await completeAssessment(symptomKey, userResponses);
    
    if (!recommendations) {
      addMessage("⚠️ Unable to generate recommendations. Please consult with a healthcare professional.", true);
      setIsLoading(false);
      return;
    }

    setIsLoading(false);

    if (recommendations.is_emergency) {
      handleEmergencyResponse();
      return;
    }

    await addTypingMessage("Based on your responses, here's my assessment:");

    // Display recommendations
    for (const rec of recommendations.recommendations) {
      if (rec.trim()) { // Skip empty strings
        await addTypingMessage(rec, 1000);
      }
    }

    // Display AI insights if available
    if (recommendations.ai_insights) {
      await addTypingMessage("🤖 AI-Enhanced Insights:", 1500);
      await addTypingMessage(recommendations.ai_insights, 2000);
    }

    // Add urgency level indicator
    if (recommendations.urgency_level === 'HIGH') {
      await addTypingMessage("⚠️ Urgency Level: HIGH - Seek medical attention promptly", 1500);
    } else if (recommendations.urgency_level === 'MEDIUM') {
      await addTypingMessage("⚠️ Urgency Level: MEDIUM - Consider medical consultation", 1500);
    }

    await addTypingMessage("Remember: This is general guidance only. Always consult with a healthcare professional for proper medical advice.", 2000);
    
    addMessage("", true, [
      { value: 'restart', text: '🔄 Check another symptom' },
      { value: 'complete', text: '✅ I\'m done' }
    ]);
    
    setCurrentStep('complete');
  };

  const handleUserResponse = async (value) => {
    // Add user message
    const selectedOption = messages[messages.length - 1].options?.find(opt => opt.value === value);
    if (selectedOption) {
      setMessages(prev => [...prev, {
        id: Date.now(),
        text: selectedOption.text,
        isBot: false,
        timestamp: new Date()
      }]);
    }

    // Handle different steps
    switch (currentStep) {
      case 'welcome':
        if (value === 'emergency') {
          handleEmergencyResponse();
        } else if (value === 'continue') {
          setCurrentStep('symptom_selection');
          await handleSymptomSelection();
        }
        break;

      case 'symptom_selection':
        if (value === 'describe') {
          await handleSymptomDescription();
        } else if (value === 'categories') {
          const symptomOptions = availableSymptoms.map(symptom => ({
            value: symptom.key,
            text: symptom.name
          }));
          addMessage("", true, [...symptomOptions, { value: 'other', text: 'Something else/Not sure' }]);
        } else if (value === 'other') {
          await addTypingMessage("For symptoms not listed, I recommend consulting with a healthcare professional directly.");
          await addTypingMessage("They can provide proper evaluation and guidance for your specific situation.");
          setCurrentStep('complete');
        } else {
          setCurrentStep('assessment');
          setCurrentQuestionIndex(0);
          setUserResponses({});
          await handleQuestionFlow(value);
        }
        break;

      case 'assessment':
        // Submit answer to API
        if (currentSymptom && currentQuestionIndex < currentSymptom.questions.length) {
          const currentQuestion = currentSymptom.questions[currentQuestionIndex];
          await submitAnswer(currentQuestion.id, value);
          
          // Update local responses
          const newResponses = { ...userResponses, [currentQuestion.id]: value };
          setUserResponses(newResponses);
          
          // Check for emergency flags
          const selectedAnswer = currentQuestion.options.find(opt => opt.value === value);
          if (selectedAnswer?.emergency) {
            handleEmergencyResponse();
            return;
          }
          
          // Move to next question
          setCurrentQuestionIndex(prev => prev + 1);
          
          // Continue with next question or complete assessment
          const symptomKey = availableSymptoms.find(s => s.name === currentSymptom.name)?.key;
          await handleQuestionFlow(symptomKey);
        }
        break;

      case 'complete':
        if (value === 'restart') {
          // Reset state
          setCurrentStep('symptom_selection');
          setUserResponses({});
          setCurrentSymptom(null);
          setCurrentQuestionIndex(0);
          
          // Create new session
          await createSession();
          await handleSymptomSelection();
        } else if (value === 'complete') {
          await addTypingMessage("Thank you for using the Health Symptom Checker. Stay healthy! 🌟");
          await addTypingMessage("Remember: When in doubt, consult with a healthcare professional.");
        }
        break;
    }
  };

  useEffect(() => {
    if (currentStep === 'welcome') {
      handleWelcome();
    }
  }, [currentStep]);

  return (
    <div className="max-w-md mx-auto bg-white shadow-2xl rounded-2xl overflow-hidden h-screen flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-teal-500 p-4 text-white">
        <div className="flex items-center gap-3">
          <div className="bg-white bg-opacity-20 p-2 rounded-full">
            <Heart className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold">Health Assistant</h1>
            <p className="text-blue-100 text-sm">Preliminary Symptom Checker</p>
          </div>
        </div>
        <div className="mt-3 text-xs bg-white bg-opacity-10 rounded-lg p-2">
          <div className="flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            <span>Not a substitute for professional medical advice</span>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.isBot ? 'justify-start' : 'justify-end'}`}>
            <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
              message.isBot 
                ? message.isEmergency 
                  ? 'bg-red-500 text-white' 
                  : 'bg-white text-gray-800 border border-gray-200'
                : 'bg-blue-500 text-white'
            }`}>
              {message.isEmergency && (
                <div className="flex items-center gap-2 mb-2">
                  <Phone className="w-5 h-5 animate-bounce" />
                  <span className="font-bold">EMERGENCY</span>
                </div>
              )}
              <div className="whitespace-pre-line text-sm leading-relaxed">
                {message.text}
              </div>
              {message.options && (
                <div className="mt-3 space-y-2">
                  {message.options.map((option, index) => (
                    <button
                      key={index}
                      onClick={() => handleUserResponse(option.value)}
                      className={`w-full text-left p-3 rounded-xl text-sm transition-all duration-200 ${
                        option.emergency 
                          ? 'bg-red-50 hover:bg-red-100 text-red-700 border border-red-200' 
                          : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 hover:shadow-sm'
                      }`}
                    >
                      {option.text}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl shadow-sm">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-500 animate-pulse" />
                <span className="text-gray-500 text-sm">Typing...</span>
              </div>
            </div>
          </div>
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-blue-50 border border-blue-200 px-4 py-3 rounded-2xl shadow-sm">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-blue-500 animate-spin" />
                <span className="text-blue-700 text-sm">Processing your request...</span>
              </div>
            </div>
          </div>
        )}

        {isWaitingForDescription && (
          <div className="flex justify-end">
            <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm bg-blue-500 text-white">
              <div className="text-sm mb-2">Please describe your symptoms:</div>
              <textarea
                placeholder="Type your symptoms here..."
                className="w-full p-2 rounded-lg text-gray-800 text-sm resize-none"
                rows="3"
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const description = e.target.value.trim();
                    if (description) {
                      setMessages(prev => [...prev, {
                        id: Date.now(),
                        text: description,
                        isBot: false,
                        timestamp: new Date()
                      }]);
                      processSymptomDescription(description);
                      e.target.value = '';
                    }
                  }
                }}
              />
              <div className="text-xs mt-1 opacity-75">Press Enter to send</div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Footer */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <Clock className="w-3 h-3" />
            <span>Always consult healthcare professionals for medical concerns</span>
          </div>
          
          {!sessionId && (
            <div className="text-xs text-red-500 bg-red-50 rounded-lg p-2">
              <div className="flex items-center justify-center gap-1">
                <AlertTriangle className="w-3 h-3" />
                <span>Backend connection required - ensure Python API is running on port 8000</span>
              </div>
            </div>
          )}
          
          {sessionId && (
            <div className="text-xs text-green-600 bg-green-50 rounded-lg p-2">
              <div className="flex items-center justify-center gap-1">
                <Heart className="w-3 h-3" />
                <span>Connected to health assessment API</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default HealthSymptomChecker;
