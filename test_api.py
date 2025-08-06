#!/usr/bin/env python3
"""
סקריפט בדיקה עבור LegalGPT API
בודק את כל הפונקציות העיקריות של המערכת
"""

import requests
import json
import time
from datetime import datetime

# הגדרות
API_BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

def test_health_check():
    """בדיקת בריאות המערכת"""
    print("🏥 בודק בריאות המערכת...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ המערכת פעילה ותקינה!")
            print(f"   תגובה: {response.json()}")
            return True
        else:
            print(f"❌ שגיאה בבדיקת בריאות: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ לא ניתן להתחבר לשרת. ודא שהשרת פועל על פורט 8000")
        return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_categories():
    """בדיקת קטגוריות משפטיות"""
    print("\n📋 בודק קטגוריות משפטיות...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/categories/")
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ נמצאו {categories['total']} קטגוריות משפטיות")
            for category in categories['categories'][:3]:  # הצג 3 ראשונות
                print(f"   📂 {category['name']}: {category['description']}")
            return True
        else:
            print(f"❌ שגיאה בקבלת קטגוריות: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_templates():
    """בדיקת תבניות מסמכים"""
    print("\n📄 בודק תבניות מסמכים...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/templates/")
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ נמצאו {templates['total']} תבניות מסמכים")
            for template in templates['templates']:
                print(f"   📝 {template['name']}: {template['description']}")
            return True
        else:
            print(f"❌ שגיאה בקבלת תבניות: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_document_generation():
    """בדיקת יצירת מסמך"""
    print("\n🏗️ בודק יצירת מסמך...")
    try:
        # נתונים לדוגמה למכתב פיטורין
        document_data = {
            "template_name": "employment_termination_letter",
            "data": {
                "employee_name": "יוסי כהן",
                "employer_name": "חברת הטכנולוגיה בע\"מ",
                "employer_address": "רחוב הרצל 123, תל אביב",
                "termination_date": "15/01/2024",
                "total_amount": "25000",
                "employee_phone": "050-1234567",
                "employee_email": "yossi.cohen@email.com"
            },
            "format_type": "html",
            "style": "formal",
            "language": "hebrew"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/documents/generate",
            headers=HEADERS,
            json=document_data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ מסמך נוצר בהצלחה!")
                print(f"   📁 שם קובץ: {result.get('filename')}")
                print(f"   📊 גודל: {result.get('size_bytes')} bytes")
                print(f"   🎨 פורמט: {result.get('format')}")
                return True
            else:
                print(f"❌ שגיאה ביצירת מסמך: {result.get('error')}")
                return False
        else:
            print(f"❌ שגיאה בבקשה: {response.status_code}")
            print(f"   תגובה: {response.text}")
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_chat_api():
    """בדיקת API הצ'אט (בסיסי)"""
    print("\n💬 בודק API הצ'אט...")
    try:
        chat_data = {
            "message": "פוטרו אותי מהעבודה ולא ברור לי מה מגיע לי",
            "language_preference": "hebrew"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/chat/send",
            headers=HEADERS,
            json=chat_data,
            timeout=30  # 30 שניות timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ הצ'אט עובד!")
            print(f"   🎯 קטגוריה שזוהתה: {result.get('detected_category')}")
            print(f"   🎯 רמת ביטחון: {result.get('confidence_score', 0):.2f}")
            if result.get('suggested_questions'):
                print(f"   ❓ שאלות מוצעות: {len(result['suggested_questions'])}")
            return True
        else:
            print(f"❌ שגיאה בצ'אט: {response.status_code}")
            print(f"   תגובה: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("⏰ הבקשה עברה timeout - ייתכן שחסר מפתח OpenAI")
        return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_documents_list():
    """בדיקת רשימת מסמכים"""
    print("\n📚 בודק רשימת מסמכים...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/documents/")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ נמצאו {result['total']} מסמכים במערכת")
            return True
        else:
            print(f"❌ שגיאה בקבלת רשימת מסמכים: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def main():
    """הפעלת כל הבדיקות"""
    print("🚀 מתחיל בדיקות LegalGPT API")
    print("=" * 50)
    
    start_time = time.time()
    tests_passed = 0
    total_tests = 6
    
    # הפעלת הבדיקות
    tests = [
        test_health_check,
        test_categories,
        test_templates,
        test_document_generation,
        test_documents_list,
        test_chat_api,
    ]
    
    for test in tests:
        if test():
            tests_passed += 1
        time.sleep(0.5)  # המתנה קצרה בין בדיקות
    
    # סיכום
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 סיכום הבדיקות:")
    print(f"✅ עברו: {tests_passed}/{total_tests}")
    print(f"❌ נכשלו: {total_tests - tests_passed}/{total_tests}")
    print(f"⏱️ זמן ביצוע: {duration:.2f} שניות")
    
    if tests_passed == total_tests:
        print("\n🎉 כל הבדיקות עברו בהצלחה! LegalGPT מוכן לשימוש!")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} בדיקות נכשלו. בדוק את ההגדרות והלוגים.")
        
        if tests_passed < 3:
            print("\n💡 טיפים לפתרון בעיות:")
            print("   1. ודא שהשרת פועל: python -m uvicorn main:app --reload")
            print("   2. בדוק שקובץ .env קיים ומכיל מפתח OpenAI")
            print("   3. ודא שהתלויות מותקנות: pip install -r requirements.txt")

if __name__ == "__main__":
    main()