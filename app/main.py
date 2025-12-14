from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import time

from app.config import settings
from app.api.routes import voice, chat, schemes, eligibility, session

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    logger.info("Starting Government Scheme Navigator API...")
    logger.info(f"Environment: {'Development' if settings.DEBUG else 'Production'}")
    
    # Initialize services here (database connections, etc.)
    # await init_database()
    # await init_redis()
    
    yield
    
    # Cleanup
    logger.info("Shutting down API...")
    # await close_database()
    # await close_redis()


# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Voice-Assisted API for navigating government schemes in India",
    version="1.0.0",
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    openapi_url=f"/api/{settings.API_VERSION}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time-Ms"] = str(round(process_time, 2))
    return response


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "type": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "type": "internal_error",
                "message": "An unexpected error occurred. Please try again later."
            }
        }
    )


# Root endpoints
@app.get("/")
async def root():
    return {
        "message": "Government Scheme Navigator API",
        "version": "1.0.0",
        "docs": f"/api/{settings.API_VERSION}/docs",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "environment": "development" if settings.DEBUG else "production"
    }


# Include routers
app.include_router(
    voice.router,
    prefix=f"/api/{settings.API_VERSION}/voice",
    tags=["Voice Processing"]
)

app.include_router(
    chat.router,
    prefix=f"/api/{settings.API_VERSION}/chat",
    tags=["Chat & Query"]
)

app.include_router(
    schemes.router,
    prefix=f"/api/{settings.API_VERSION}/schemes",
    tags=["Schemes"]
)

app.include_router(
    eligibility.router,
    prefix=f"/api/{settings.API_VERSION}/eligibility",
    tags=["Eligibility"]
)

app.include_router(
    session.router,
    prefix=f"/api/{settings.API_VERSION}/session",
    tags=["Session Management"]
)


# Audio file serving endpoint
@app.get("/api/{version}/audio/{filename}")
async def serve_audio_file(version: str, filename: str):
    """Serve generated audio files"""
    audio_path = Path(settings.AUDIO_STORAGE_PATH) / filename
    
    if not audio_path.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Audio file not found"}
        )
    
    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "public, max-age=3600",
            "Content-Disposition": f"inline; filename={filename}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
