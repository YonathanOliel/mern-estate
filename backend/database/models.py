"""
Database models for LegalGPT
Basic models for future database integration
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class ChatSession(BaseModel):
    """מודל לסשן צ'אט"""
    id: str
    user_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[str] = None
    status: str = "active"  # active, completed, archived

class ChatMessage(BaseModel):
    """מודל להודעת צ'אט"""
    id: str
    session_id: str
    content: str
    sender: str  # user, ai
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class User(BaseModel):
    """מודל למשתמש"""
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    is_active: bool = True

class Document(BaseModel):
    """מודל למסמך"""
    id: str
    user_id: Optional[str] = None
    template_name: str
    filename: str
    file_path: str
    format_type: str  # pdf, docx, html
    created_at: datetime
    size_bytes: int
    metadata: Optional[Dict[str, Any]] = None

# Placeholder functions for future database integration
async def save_chat_message(request, response):
    """Save chat message to database (placeholder)"""
    pass

async def get_session_history(session_id: str):
    """Get chat history for session (placeholder)"""
    return []

async def delete_chat_session(session_id: str):
    """Delete chat session (placeholder)"""
    pass

async def save_feedback(session_id: str, message_id: str, feedback_type: str, comment: str):
    """Save user feedback (placeholder)"""
    pass