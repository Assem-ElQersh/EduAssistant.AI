from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up AI Educational Platform...")
    # Create database tables
    from app.db.database import engine, Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down AI Educational Platform...")

# Create FastAPI app
app = FastAPI(
    title="AI Educational Platform",
    description="Advanced AI-powered learning platform for Japanese language education",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow everything for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
from app.api.routes import auth
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])

@app.get("/")
async def root():
    return {
        "message": "AI Educational Platform API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Educational Platform is running"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )