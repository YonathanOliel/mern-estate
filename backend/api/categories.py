from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from legal.categories import LegalCategoryDetector

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize category detector
category_detector = LegalCategoryDetector()

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_categories():
    """קבלת רשימת כל הקטגוריות המשפטיות הזמינות"""
    try:
        categories = await category_detector.get_all_categories()
        return categories
    except Exception as e:
        logger.error(f"Error getting categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת רשימת הקטגוריות"
        )

@router.get("/{category_id}")
async def get_category_info(category_id: str):
    """קבלת מידע מפורט על קטגוריה ספציפית"""
    try:
        category_info = category_detector.get_category_info(category_id)
        if not category_info:
            raise HTTPException(
                status_code=404,
                detail=f"קטגוריה {category_id} לא נמצאה"
            )
        return category_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting category info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת מידע על הקטגוריה"
        )

@router.get("/{category_id}/related")
async def get_related_categories(category_id: str):
    """קבלת קטגוריות קשורות לקטגוריה נתונה"""
    try:
        related = await category_detector.suggest_related_categories(category_id)
        return {
            "category_id": category_id,
            "related_categories": related
        }
    except Exception as e:
        logger.error(f"Error getting related categories: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת קטגוריות קשורות"
        )