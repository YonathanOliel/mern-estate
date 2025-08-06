import os
import io
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pathlib import Path
import json

# Document generation libraries
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from jinja2 import Template, Environment, FileSystemLoader

logger = logging.getLogger(__name__)

class DocumentGenerator:
    """
    מערכת יצירת מסמכים משפטיים בפורמטים שונים
    תומכת ב-PDF, Word, HTML עם תמיכה מלאה בעברית
    """
    
    def __init__(self):
        """אתחול מחולל המסמכים"""
        self.output_dir = Path(os.getenv('DOCUMENTS_OUTPUT_PATH', './generated_documents'))
        self.templates_dir = Path(os.getenv('TEMPLATES_PATH', '../templates'))
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize Jinja2 environment for templates
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            enable_async=True
        )
        
        # Hebrew font support for PDF
        self.hebrew_font_path = self._setup_hebrew_fonts()
        
        # Document styles
        self.styles = self._setup_styles()

    async def generate_document(
        self,
        template_name: str,
        data: Dict[str, Any],
        format_type: str = "pdf",
        style: str = "formal",
        language: str = "hebrew"
    ) -> Dict[str, Any]:
        """
        יצירת מסמך משפטי לפי תבנית
        
        Args:
            template_name: שם התבנית
            data: נתונים למילוי התבנית
            format_type: סוג הקובץ (pdf, docx, html)
            style: סגנון המסמך (formal, simple)
            language: שפת המסמך
            
        Returns:
            מידע על המסמך שנוצר
        """
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{template_name}_{timestamp}.{format_type}"
            file_path = self.output_dir / filename
            
            # Add metadata to data
            enhanced_data = self._enhance_data(data, style, language)
            
            # Generate document based on format
            if format_type.lower() == "pdf":
                await self._generate_pdf(template_name, enhanced_data, file_path)
            elif format_type.lower() == "docx":
                await self._generate_docx(template_name, enhanced_data, file_path)
            elif format_type.lower() == "html":
                await self._generate_html(template_name, enhanced_data, file_path)
            else:
                raise ValueError(f"פורמט לא נתמך: {format_type}")
            
            # Return document information
            return {
                "success": True,
                "filename": filename,
                "file_path": str(file_path),
                "size_bytes": file_path.stat().st_size,
                "created_at": datetime.now().isoformat(),
                "format": format_type,
                "template": template_name,
                "language": language,
                "style": style
            }
            
        except Exception as e:
            logger.error(f"Error generating document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "template": template_name,
                "format": format_type
            }

    async def _generate_pdf(self, template_name: str, data: Dict[str, Any], file_path: Path):
        """יצירת מסמך PDF עם תמיכה בעברית"""
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        styles = getSampleStyleSheet()
        
        # Hebrew style
        hebrew_style = ParagraphStyle(
            'Hebrew',
            parent=styles['Normal'],
            fontName='Hebrew' if self.hebrew_font_path else 'Helvetica',
            fontSize=12,
            alignment=2,  # Right alignment for Hebrew
            spaceAfter=12
        )
        
        # Title style
        title_style = ParagraphStyle(
            'HebrewTitle',
            parent=hebrew_style,
            fontSize=18,
            alignment=1,  # Center alignment
            spaceAfter=24,
            textColor=colors.black
        )
        
        # Load and render template
        template = self.jinja_env.get_template(f"{template_name}.html")
        content = await template.render_async(**data)
        
        # Add title
        if data.get('title'):
            story.append(Paragraph(data['title'], title_style))
            story.append(Spacer(1, 12))
        
        # Add content paragraphs
        paragraphs = content.split('\n')
        for paragraph in paragraphs:
            if paragraph.strip():
                story.append(Paragraph(paragraph, hebrew_style))
                story.append(Spacer(1, 6))
        
        # Add signature section if needed
        if data.get('include_signature', True):
            story.append(Spacer(1, 24))
            story.append(Paragraph("חתימה: ________________", hebrew_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"תאריך: {datetime.now().strftime('%d/%m/%Y')}", hebrew_style))
        
        # Build PDF
        doc.build(story)

    async def _generate_docx(self, template_name: str, data: Dict[str, Any], file_path: Path):
        """יצירת מסמך Word עם תמיכה בעברית"""
        
        # Create Word document
        doc = Document()
        
        # Set Hebrew language and RTL
        doc.settings.default_language = "he-IL"
        
        # Load and render template
        template = self.jinja_env.get_template(f"{template_name}.html")
        content = await template.render_async(**data)
        
        # Add title
        if data.get('title'):
            title = doc.add_heading(data['title'], level=1)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add content
        paragraphs = content.split('\n')
        for paragraph_text in paragraphs:
            if paragraph_text.strip():
                p = doc.add_paragraph(paragraph_text)
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT  # Hebrew RTL
        
        # Add signature section
        if data.get('include_signature', True):
            doc.add_paragraph("")  # Empty line
            sig_p = doc.add_paragraph("חתימה: ________________")
            sig_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            
            date_p = doc.add_paragraph(f"תאריך: {datetime.now().strftime('%d/%m/%Y')}")
            date_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        
        # Save document
        doc.save(str(file_path))

    async def _generate_html(self, template_name: str, data: Dict[str, Any], file_path: Path):
        """יצירת מסמך HTML עם תמיכה בעברית"""
        
        # Load template
        template = self.jinja_env.get_template(f"{template_name}.html")
        content = await template.render_async(**data)
        
        # Create full HTML document
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{data.get('title', 'מסמך משפטי')}</title>
            <style>
                body {{
                    font-family: 'Arial', 'Hebrew', sans-serif;
                    line-height: 1.6;
                    margin: 40px;
                    direction: rtl;
                    text-align: right;
                }}
                .header {{
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 30px;
                }}
                .content {{
                    font-size: 14px;
                    margin-bottom: 20px;
                }}
                .signature {{
                    margin-top: 40px;
                }}
                @media print {{
                    body {{ margin: 20px; }}
                }}
            </style>
        </head>
        <body>
            {content}
            {self._get_signature_html() if data.get('include_signature', True) else ''}
        </body>
        </html>
        """
        
        # Save HTML file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def _enhance_data(self, data: Dict[str, Any], style: str, language: str) -> Dict[str, Any]:
        """הוספת מטא-דאטה למסמך"""
        enhanced = data.copy()
        
        # Add current date
        enhanced['current_date'] = datetime.now().strftime('%d/%m/%Y')
        enhanced['current_time'] = datetime.now().strftime('%H:%M')
        
        # Add style and language
        enhanced['style'] = style
        enhanced['language'] = language
        
        # Add Hebrew months for date formatting
        enhanced['hebrew_months'] = {
            1: 'ינואר', 2: 'פברואר', 3: 'מרץ', 4: 'אפריל',
            5: 'מאי', 6: 'יוני', 7: 'יולי', 8: 'אוגוסט',
            9: 'ספטמבר', 10: 'אוקטובר', 11: 'נובמבר', 12: 'דצמבר'
        }
        
        # Add common legal phrases
        enhanced['legal_phrases'] = {
            'respectfully': 'בכבוד רב',
            'sincerely': 'בברכה',
            'urgent': 'דחוף',
            'confidential': 'חסוי',
            'copy_to': 'העתק:',
            'subject': 'נושא:'
        }
        
        return enhanced

    def _setup_hebrew_fonts(self) -> Optional[str]:
        """הגדרת פונטים עבריים ל-PDF"""
        try:
            # Try to register Hebrew fonts
            font_paths = [
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/System/Library/Fonts/Arial.ttf",
                "/Windows/Fonts/arial.ttf"
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('Hebrew', font_path))
                    return font_path
            
            logger.warning("No Hebrew fonts found, using default fonts")
            return None
            
        except Exception as e:
            logger.warning(f"Could not setup Hebrew fonts: {str(e)}")
            return None

    def _setup_styles(self) -> Dict[str, Any]:
        """הגדרת סגנונות למסמכים"""
        return {
            "formal": {
                "font_size": 12,
                "line_spacing": 1.5,
                "margins": {"top": 2.5, "bottom": 2.5, "left": 2.5, "right": 2.5},
                "header_size": 18
            },
            "simple": {
                "font_size": 11,
                "line_spacing": 1.2,
                "margins": {"top": 2, "bottom": 2, "left": 2, "right": 2},
                "header_size": 16
            }
        }

    def _get_signature_html(self) -> str:
        """HTML לחתימה"""
        return f"""
        <div class="signature">
            <p>חתימה: ________________</p>
            <p>תאריך: {datetime.now().strftime('%d/%m/%Y')}</p>
        </div>
        """

    async def get_available_templates(self) -> List[Dict[str, Any]]:
        """קבלת רשימת התבניות הזמינות"""
        templates = []
        
        try:
            for template_file in self.templates_dir.glob("*.html"):
                template_name = template_file.stem
                
                # Try to load template metadata
                metadata_file = self.templates_dir / f"{template_name}.json"
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                else:
                    metadata = {"name": template_name, "description": "תבנית משפטית"}
                
                templates.append({
                    "id": template_name,
                    "name": metadata.get("name", template_name),
                    "description": metadata.get("description", ""),
                    "category": metadata.get("category", "general"),
                    "required_fields": metadata.get("required_fields", []),
                    "optional_fields": metadata.get("optional_fields", [])
                })
                
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
        
        return templates