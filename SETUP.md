# 🚀 מדריך התקנה והפעלה - LegalGPT

## 📋 דרישות מוקדמות

לפני התחלת ההתקנה, ודא שמותקנים במערכת שלך:

### תוכנות נדרשות:
- **Python 3.9+** - [הורד כאן](https://www.python.org/downloads/)
- **Node.js 16+** - [הורד כאן](https://nodejs.org/)
- **Git** - [הורד כאן](https://git-scm.com/)

### API Keys נדרשים:
- **OpenAI API Key** - [קבל כאן](https://platform.openai.com/api-keys)

## 🏗️ התקנה מהירה

### שלב 1: הורד את הפרויקט
```bash
git clone https://github.com/yourusername/legalgpt.git
cd legalgpt
```

### שלב 2: הפעלה אוטומטית
```bash
./start.sh
```

הסקריפט יבצע את כל ההתקנה והפעלה אוטומטית!

## 🔧 התקנה ידנית (אופציונלי)

### בקאנד (Python/FastAPI)

1. **יצירת סביבה וירטואלית:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# או
venv\Scripts\activate     # Windows
```

2. **התקנת תלויות:**
```bash
pip install -r requirements.txt
```

3. **הגדרת משתני סביבה:**
```bash
cp .env.example .env
```
ערוך את קובץ `.env` והוסף את המפתח של OpenAI:
```
OPENAI_API_KEY=your-openai-api-key-here
```

4. **הפעלת השרת:**
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### פרונטאנד (React/TypeScript)

1. **התקנת תלויות:**
```bash
cd frontend
npm install
```

2. **הפעלת השרת:**
```bash
npm run dev
```

## 🌐 גישה למערכת

לאחר ההפעלה המוצלחת:

- **אפליקציה:** http://localhost:3000
- **API Backend:** http://localhost:8000
- **תיעוד API:** http://localhost:8000/docs

## 🧪 בדיקת המערכת

### בדיקת הבקאנד:
```bash
curl http://localhost:8000/health
```
תגובה צפויה:
```json
{
  "status": "healthy",
  "service": "LegalGPT API",
  "version": "1.0.0"
}
```

### בדיקת הפרונטאנד:
פתח דפדפן וגש לכתובת: http://localhost:3000

## 📁 מבנה הפרויקט

```
LegalGPT/
├── backend/                 # שרת Python (FastAPI)
│   ├── main.py             # נקודת כניסה ראשית
│   ├── api/                # נתיבי API
│   │   ├── chat.py         # צ'אט עם AI
│   │   ├── documents.py    # ניהול מסמכים
│   │   ├── categories.py   # קטגוריות משפטיות
│   │   └── users.py        # ניהול משתמשים
│   ├── ai/                 # מודולי בינה מלאכותית
│   │   ├── legal_ai.py     # AI משפטי ראשי
│   │   └── hebrew_processor.py # עיבוד עברית
│   ├── legal/              # לוגיקה משפטית
│   │   └── categories.py   # זיהוי קטגוריות
│   ├── documents/          # יצירת מסמכים
│   │   └── generator.py    # מחולל מסמכים
│   └── requirements.txt    # תלויות Python
├── frontend/               # ממשק משתמש (React)
│   ├── src/
│   │   ├── components/     # רכיבי UI
│   │   ├── pages/          # דפי האפליקציה
│   │   ├── services/       # שירותי API
│   │   └── main.tsx        # נקודת כניסה
│   └── package.json        # תלויות Node.js
├── templates/              # תבניות מסמכים משפטיים
│   ├── employment_termination_letter.html
│   ├── rental_contract.html
│   └── consumer_complaint_letter.html
├── start.sh               # סקריפט הפעלה אוטומטית
└── README.md              # תיעוד הפרויקט
```

## 🎯 פיצ'רים זמינים

### ✅ מוכנים לשימוש:
- 🏠 **דף בית** - מבוא ונתיבים לפיצ'רים
- 📋 **קטגוריות משפטיות** - 6 תחומי משפט עיקריים
- 🔧 **API מלא** - עם תיעוד אוטומטי
- 📄 **תבניות מסמכים** - 3 תבניות בסיסיות
- 🎨 **ממשק יפה** - עיצוב מודרני עם תמיכה בעברית

### 🚧 בפיתוח:
- 💬 **צ'אט AI** - יושלם בקרוב
- 📊 **ניהול משתמשים** - מערכת רישום והתחברות
- 📈 **דשבורד אישי** - מעקב אחר מסמכים ופעילות

## 🐛 פתרון בעיות נפוצות

### שגיאת "Port already in use"
```bash
# הרג תהליכים על פורט 8000
lsof -ti:8000 | xargs kill -9

# הרג תהליכים על פורט 3000  
lsof -ti:3000 | xargs kill -9
```

### שגיאת "Module not found"
```bash
# בקאנד
cd backend
pip install -r requirements.txt

# פרונטאנד
cd frontend
npm install
```

### בעיות עם OpenAI API
1. ודא שהמפתח נכון בקובץ `.env`
2. בדוק שיש לך קרדיט ב-OpenAI
3. ודא שהמפתח פעיל

## 🔒 אבטחה

### הגדרות ייצור:
1. **שנה מפתחות סודיים** בקובץ `.env`
2. **הגדר CORS** לדומיינים ספציפיים
3. **הפעל HTTPS** עם תעודות SSL
4. **הגבל גישה לפורטים** ברמת הרשת

### משתני סביבה חשובים:
```bash
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
API_DEBUG=False  # בייצור
```

## 📞 תמיכה

### דרכי יצירת קשר:
- 📧 **אימייל:** support@legalgpt.co.il
- 🐛 **באגים:** פתח issue ב-GitHub
- 💡 **הצעות:** discussions ב-GitHub

### לוגים ודיבאג:
- **לוגי בקאנד:** `backend/logs/legalgpt.log`
- **לוגי פרונטאנד:** קונסולת הדפדפן (F12)

## 🚀 פיתוח נוסף

### הוספת תבנית מסמך חדשה:
1. צור קובץ HTML ב-`templates/`
2. צור קובץ JSON עם מטא-דאטה
3. הוסף לרשימה ב-`legal/categories.py`

### הוספת קטגוריה משפטית:
1. ערוך את `LegalCategory` enum
2. הוסף מילות מפתח ב-`category_keywords`
3. הוסף לממשק ב-`CategoriesPage.tsx`

---

**🎉 מזל טוב! LegalGPT מוכן לשימוש!**

המערכת שלך כוללת בינה מלאכותית מתקדמת, יצירת מסמכים משפטיים, וממשק משתמש יפהפה - הכל בעברית מלאה! 🇮🇱⚖️