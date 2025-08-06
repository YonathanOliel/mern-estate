from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

from documents.generator import DocumentGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize document generator for template access
doc_generator = DocumentGenerator()

@router.get("/")
async def get_all_templates():
    """קבלת רשימת כל התבניות הזמינות"""
    try:
        templates = await doc_generator.get_available_templates()
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת רשימת התבניות"
        )

@router.get("/{template_id}")
async def get_template_details(template_id: str):
    """קבלת פרטים מלאים על תבנית ספציפית"""
    try:
        templates = await doc_generator.get_available_templates()
        template = next((t for t in templates if t["id"] == template_id), None)
        
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"תבנית {template_id} לא נמצאה"
            )
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת פרטי התבנית"
        )

@router.get("/category/{category_id}")
async def get_templates_by_category(category_id: str):
    """קבלת תבניות לפי קטגוריה"""
    try:
        all_templates = await doc_generator.get_available_templates()
        category_templates = [t for t in all_templates if t.get("category") == category_id]
        
        return {
            "category": category_id,
            "templates": category_templates,
            "total": len(category_templates)
        }
        
    except Exception as e:
        logger.error(f"Error getting templates by category: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת תבניות לפי קטגוריה"
        )