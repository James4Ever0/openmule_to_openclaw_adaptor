from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from .config import get_settings
from .database import init_db
from .handlers import (
    auth_router,
    task_router,
    bid_router,
    order_router,
    message_router,
    ai_router,
    cs_router,
    user_router,
)
from .websocket.handlers import websocket_endpoint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up OpenMule Backend...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down OpenMule Backend...")


app = FastAPI(
    title="OpenMule Backend",
    description="Backend API for OpenMule platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "OpenMule Backend API",
        "version": "1.0.0",
        "status": "running"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Backend is running smoothly"
    }


# API routes
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(task_router, prefix="/api/v1")
app.include_router(bid_router, prefix="/api/v1")
app.include_router(order_router, prefix="/api/v1")
app.include_router(message_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(cs_router, prefix="/api/v1")

# WebSocket endpoint
app.websocket("/api/v1/ws")(websocket_endpoint)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        log_level="info"
    )
