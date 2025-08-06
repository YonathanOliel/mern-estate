from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import os
from pathlib import Path

from documents.generator import DocumentGenerator

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize document generator
doc_generator = DocumentGenerator()

class DocumentRequest(BaseModel):
    template_name: str
    data: Dict[str, Any]
    format_type: str = "pdf"  # pdf, docx, html
    style: str = "formal"  # formal, simple
    language: str = "hebrew"

class DocumentResponse(BaseModel):
    success: bool
    filename: Optional[str] = None
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[str] = None
    format: Optional[str] = None
    template: Optional[str] = None
    language: Optional[str] = None
    style: Optional[str] = None
    error: Optional[str] = None

@router.post("/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest):
    """יצירת מסמך משפטי חדש"""
    try:
        result = await doc_generator.generate_document(
            template_name=request.template_name,
            data=request.data,
            format_type=request.format_type,
            style=request.style,
            language=request.language
        )
        
        return DocumentResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"שגיאה ביצירת המסמך: {str(e)}"
        )

@router.get("/templates")
async def get_available_templates():
    """קבלת רשימת התבניות הזמינות"""
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

@router.get("/download/{filename}")
async def download_document(filename: str):
    """הורדת מסמך שנוצר"""
    try:
        file_path = doc_generator.output_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="הקובץ לא נמצא"
            )
        
        # Determine media type based on file extension
        media_type_mapping = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.html': 'text/html'
        }
        
        file_extension = file_path.suffix.lower()
        media_type = media_type_mapping.get(file_extension, 'application/octet-stream')
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בהורדת המסמך"
        )

@router.get("/preview/{filename}")
async def preview_document(filename: str):
    """תצוגה מקדימה של מסמך (HTML)"""
    try:
        file_path = doc_generator.output_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="הקובץ לא נמצא"
            )
        
        # Only support HTML preview for now
        if not filename.lower().endswith('.html'):
            raise HTTPException(
                status_code=400,
                detail="תצוגה מקדימה זמינה רק לקבצי HTML"
            )
        
        return FileResponse(
            path=str(file_path),
            media_type='text/html'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error previewing document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בתצוגה מקדימה"
        )

@router.delete("/{filename}")
async def delete_document(filename: str):
    """מחיקת מסמך"""
    try:
        file_path = doc_generator.output_dir / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail="הקובץ לא נמצא"
            )
        
        file_path.unlink()  # Delete file
        
        return {
            "message": f"המסמך {filename} נמחק בהצלחה",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה במחיקת המסמך"
        )

@router.get("/")
async def list_documents():
    """קבלת רשימת המסמכים שנוצרו"""
    try:
        documents = []
        
        for file_path in doc_generator.output_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                documents.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "created_at": stat.st_ctime,
                    "format": file_path.suffix[1:] if file_path.suffix else "unknown"
                })
        
        # Sort by creation time (newest first)
        documents.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "documents": documents,
            "total": len(documents)
        }
        
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בקבלת רשימת המסמכים"
        )

@router.post("/validate-template")
async def validate_template_data(template_name: str, data: Dict[str, Any]):
    """בדיקת תקינות נתונים לתבנית"""
    try:
        # Get template info
        templates = await doc_generator.get_available_templates()
        template_info = next((t for t in templates if t["id"] == template_name), None)
        
        if not template_info:
            raise HTTPException(
                status_code=404,
                detail=f"תבנית {template_name} לא נמצאה"
            )
        
        # Check required fields
        missing_fields = []
        required_fields = template_info.get("required_fields", [])
        
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        validation_result = {
            "valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "template_name": template_name,
            "required_fields": required_fields,
            "optional_fields": template_info.get("optional_fields", [])
        }
        
        return validation_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating template data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="שגיאה בבדיקת תקינות הנתונים"
        )