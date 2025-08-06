#!/bin/bash

echo "🚀 מתחיל את LegalGPT - עורך הדין האישי שלך"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 לא מותקן במערכת${NC}"
    echo "אנא התקן Python 3.9 ומעלה"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js לא מותקן במערכת${NC}"
    echo "אנא התקן Node.js 16 ומעלה"
    exit 1
fi

echo -e "${BLUE}🐍 מתחיל את הבקאנד (FastAPI)...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}📦 יוצר סביבה וירטואלית...${NC}"
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment and install dependencies
echo -e "${YELLOW}📦 מתקין תלויות Python...${NC}"
cd backend
source venv/bin/activate
pip install --upgrade pip
if ! pip install -r requirements.txt; then
    echo -e "${RED}❌ שגיאה בהתקנת תלויות Python${NC}"
    echo -e "${YELLOW}💡 נסה להריץ: pip install --upgrade pip setuptools wheel${NC}"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚙️  יוצר קובץ הגדרות (.env)...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  אנא ערוך את קובץ .env והוסף את המפתח של OpenAI${NC}"
fi

# Start backend in background
echo -e "${GREEN}✅ מפעיל את השרת הבקאנד על פורט 8000...${NC}"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd ..

echo -e "${BLUE}⚛️  מתחיל את הפרונטאנד (React)...${NC}"

# Install frontend dependencies
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 מתקין תלויות Node.js...${NC}"
    cd frontend
    if ! npm install; then
        echo -e "${RED}❌ שגיאה בהתקנת תלויות Node.js${NC}"
        echo -e "${YELLOW}💡 נסה להריץ: npm cache clean --force${NC}"
        exit 1
    fi
    cd ..
fi

# Start frontend
echo -e "${GREEN}✅ מפעיל את הפרונטאנד על פורט 3000...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo -e "${GREEN}🎉 LegalGPT מופעל בהצלחה!${NC}"
echo "================================================"
echo -e "${BLUE}🌐 פתח את הדפדפן וגש לכתובת:${NC}"
echo -e "${GREEN}   Frontend: http://localhost:3000${NC}"
echo -e "${GREEN}   Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}   API Docs: http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}⚠️  לעצירת המערכת, לחץ Ctrl+C${NC}"
echo ""

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 עוצר את המערכת...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ המערכת נעצרה בהצלחה${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for processes
wait