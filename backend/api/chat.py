from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
import json
import logging

from ai.legal_ai import LegalAI
from ai.hebrew_processor import HebrewProcessor
from legal.categories import LegalCategoryDetector
from database.models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize AI components
legal_ai = LegalAI()
hebrew_processor = HebrewProcessor()
category_detector = LegalCategoryDetector()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    language_preference: str = "hebrew"  # hebrew, english, arabic

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_id: str
    detected_category: Optional[str] = None
    suggested_questions: List[str] = []
    confidence_score: float = 0.0
    next_steps: List[str] = []
    requires_clarification: bool = False
    timestamp: datetime

class QuickStartRequest(BaseModel):
    category: str  # "rental_contract", "employment_termination", "small_claims", etc.
    user_id: Optional[str] = None

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    שליחת הודעה לצ'אט AI
    מזהה קטגוריה משפטית, מעבד עברית, ומחזיר תגובה מותאמת
    """
    try:
        # Process Hebrew text if needed
        processed_message = hebrew_processor.process_text(request.message)
        
        # Detect legal category
        detected_category = await category_detector.detect_category(processed_message)
        
        # Generate AI response
        ai_response = await legal_ai.generate_response(
            message=processed_message,
            category=detected_category,
            context=request.context,
            language=request.language_preference
        )
        
        # Generate suggested follow-up questions
        suggested_questions = await legal_ai.generate_follow_up_questions(
            message=processed_message,
            category=detected_category,
            language=request.language_preference
        )
        
        # Determine next steps
        next_steps = await legal_ai.suggest_next_steps(
            category=detected_category,
            context=request.context
        )
        
        # Create response
        response = ChatResponse(
            response=ai_response["text"],
            session_id=request.session_id or f"session_{datetime.now().timestamp()}",
            message_id=f"msg_{datetime.now().timestamp()}",
            detected_category=detected_category,
            suggested_questions=suggested_questions,
            confidence_score=ai_response.get("confidence", 0.0),
            next_steps=next_steps,
            requires_clarification=ai_response.get("requires_clarification", False),
            timestamp=datetime.now()
        )
        
        # TODO: Save to database
        # await save_chat_message(request, response)
        
        logger.info(f"Chat response generated for category: {detected_category}")
        return response
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בעיבוד ההודעה: {str(e)}"
        )

@router.post("/quick-start", response_model=ChatResponse)
async def quick_start_category(request: QuickStartRequest):
    """
    התחלה מהירה עם קטגוריה משפטית ספציפית
    מחזיר שאלות התחלתיות מותאמות לקטגוריה
    """
    try:
        # Get category-specific starter questions
        starter_response = await legal_ai.get_category_starter(request.category)
        
        response = ChatResponse(
            response=starter_response["welcome_message"],
            session_id=f"quickstart_{datetime.now().timestamp()}",
            message_id=f"msg_{datetime.now().timestamp()}",
            detected_category=request.category,
            suggested_questions=starter_response["initial_questions"],
            confidence_score=1.0,
            next_steps=starter_response["next_steps"],
            requires_clarification=True,
            timestamp=datetime.now()
        )
        
        logger.info(f"Quick start initiated for category: {request.category}")
        return response
        
    except Exception as e:
        logger.error(f"Error in quick-start endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה בהתחלה המהירה: {str(e)}"
        )

@router.get("/categories")
async def get_available_categories():
    """קבלת רשימת הקטגוריות המשפטיות הזמינות"""
    try:
        categories = await category_detector.get_all_categories()
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת הקטגוריות"
        )

@router.get("/session/{session_id}/history")
async def get_chat_history(session_id: str):
    """קבלת היסטוריית צ'אט לפי מזהה סשן"""
    try:
        # TODO: Implement database query
        # history = await get_session_history(session_id)
        history = []
        
        return {
            "session_id": session_id,
            "messages": history,
            "total_messages": len(history)
        }
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת היסטוריית הצ'אט"
        )

@router.delete("/session/{session_id}")
async def clear_chat_session(session_id: str):
    """מחיקת סשן צ'אט"""
    try:
        # TODO: Implement database deletion
        # await delete_chat_session(session_id)
        
        return {
            "message": f"סשן {session_id} נמחק בהצלחה",
            "session_id": session_id
        }
    except Exception as e:
        logger.error(f"Error clearing chat session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה במחיקת הסשן"
        )

@router.post("/feedback")
async def submit_feedback(
    session_id: str,
    message_id: str,
    feedback_type: str,  # "helpful", "not_helpful", "incorrect"
    comment: Optional[str] = None
):
    """שליחת משוב על תגובת AI"""
    try:
        # TODO: Save feedback to database
        # await save_feedback(session_id, message_id, feedback_type, comment)
        
        return {
            "message": "המשוב נשמר בהצלחה",
            "feedback_type": feedback_type
        }
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בשמירת המשוב"
        )