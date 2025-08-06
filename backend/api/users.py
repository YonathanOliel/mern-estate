from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    created_at: datetime
    documents_count: int = 0

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """רישום משתמש חדש"""
    try:
        # TODO: Implement user registration with database
        # For now, return mock response
        user_id = f"user_{datetime.now().timestamp()}"
        
        return UserResponse(
            id=user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            created_at=datetime.now(),
            documents_count=0
        )
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה ברישום המשתמש"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """קבלת פרטי משתמש"""
    try:
        # TODO: Implement user lookup from database
        # For now, return mock response
        return UserResponse(
            id=user_id,
            name="משתמש לדוגמה",
            email="user@example.com",
            created_at=datetime.now(),
            documents_count=5
        )
        
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail="המשתמש לא נמצא"
        )

@router.get("/{user_id}/documents")
async def get_user_documents(user_id: str):
    """קבלת מסמכים של משתמש"""
    try:
        # TODO: Implement user documents lookup
        return {
            "user_id": user_id,
            "documents": [],
            "total": 0
        }
        
    except Exception as e:
        logger.error(f"Error getting user documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת מסמכי המשתמש"
        )