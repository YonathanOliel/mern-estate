#!/usr/bin/env python3
"""
בדיקה מהירה לוודא שכל המודולים נטענים כראוי
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)
os.chdir(backend_path)

def test_imports():
    """בדיקת imports בסיסיים"""
    print("🔍 בודק imports...")
    
    try:
        # Test basic imports
        import fastapi
        print("✅ FastAPI")
        
        import pydantic
        print("✅ Pydantic")
        
        import jinja2
        print("✅ Jinja2")
        
        import reportlab
        print("✅ ReportLab")
        
        from docx import Document
        print("✅ python-docx")
        
        # Test our modules
        from ai.hebrew_processor import HebrewProcessor
        print("✅ Hebrew Processor")
        
        from ai.legal_ai import LegalAI
        print("✅ Legal AI")
        
        from legal.categories import LegalCategoryDetector
        print("✅ Category Detector")
        
        from documents.generator import DocumentGenerator
        print("✅ Document Generator")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_basic_functionality():
    """בדיקת פונקציונליות בסיסית"""
    print("\n🧪 בודק פונקציונליות בסיסית...")
    
    try:
        # Test Hebrew processor
        from ai.hebrew_processor import HebrewProcessor
        processor = HebrewProcessor()
        
        test_text = "פוטרו אותי מהעבודה"
        processed = processor.process_text(test_text)
        print(f"✅ Hebrew processing: '{test_text}' -> '{processed}'")
        
        # Test category detector
        from legal.categories import LegalCategoryDetector
        detector = LegalCategoryDetector()
        
        # This is async, so we'll just test the initialization
        categories = detector.category_keywords
        print(f"✅ Category detector initialized with {len(categories)} categories")
        
        # Test document generator
        from documents.generator import DocumentGenerator
        generator = DocumentGenerator()
        print("✅ Document generator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    """הפעלת כל הבדיקות"""
    print("🚀 בדיקה מהירה של LegalGPT")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 כל הבדיקות עברו בהצלחה!")
        print("המערכת מוכנה להפעלה עם ./start.sh")
    else:
        print("⚠️ יש בעיות שצריך לתקן")
        print("נסה להתקין את התלויות: pip install -r backend/requirements.txt")

if __name__ == "__main__":
    main()