from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

# Import API routers
from api.chat import router as chat_router
from api.documents import router as documents_router
from api.categories import router as categories_router
from api.users import router as users_router
from api.templates import router as templates_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', './logs/legalgpt.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    # Startup
    logger.info("🚀 LegalGPT API starting up...")
    
    # Create necessary directories
    os.makedirs("./logs", exist_ok=True)
    os.makedirs(os.getenv('DOCUMENTS_OUTPUT_PATH', './generated_documents'), exist_ok=True)
    
    # Initialize database
    # from database.init_db import init_database
    # await init_database()
    
    logger.info("✅ LegalGPT API started successfully")
    yield
    
    # Shutdown
    logger.info("🛑 LegalGPT API shutting down...")

# Create FastAPI app
app = FastAPI(
    title="LegalGPT API",
    description="עורך הדין האישי שלך - API לשירותים משפטיים חכמים",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure properly in production
)

# Include API routers
app.include_router(chat_router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(templates_router, prefix="/api/v1/templates", tags=["Templates"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ברוכים הבאים ל-LegalGPT API! 🏛️⚖️",
        "description": "עורך הדין האישי שלך - שירותים משפטיים חכמים",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LegalGPT API",
        "version": "1.0.0"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler with Hebrew support"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(datetime.utcnow())
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "שגיאה פנימית בשרת. אנא נסו שוב מאוחר יותר.",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    from datetime import datetime
    
    uvicorn.run(
        "main:app",
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', 8000)),
        reload=os.getenv('API_DEBUG', 'True').lower() == 'true',
        log_level=os.getenv('LOG_LEVEL', 'info').lower()
    )