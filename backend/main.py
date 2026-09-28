from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, CORS_ORIGINS
from backend.utils.logger import get_logger
from backend.database.connection import init_db
from backend.api.routes import router as api_router
from backend.api.data_routes import router as data_router
from backend.api.auth import router as auth_router
from backend.api.core_routes import router as core_router
from backend.api.ml_routes import router as ml_router
from backend.api.dashboard import router as dashboard_router
from backend.api.chat import router as chat_router

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI app.
    Loads the ML model into memory exactly once at startup.
    Initialises the database.
    """
    logger.info("Initializing database...")
    init_db()
    
    yield
    
    logger.info("Shutting down Application...")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

# Global Exception Handler (Never leak stack traces)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    
    logger.error(f"Unhandled exception during request {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers={"Access-Control-Allow-Origin": "*"}
    )

# Register API Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(core_router, prefix="/api", tags=["Core Operations"])
app.include_router(data_router, prefix="/api/data", tags=["Data Ingestion & Management"])
app.include_router(ml_router, prefix="/api/ml", tags=["Machine Learning & Analysis"])
app.include_router(ml_router, prefix="/api/survival", tags=["Survival Analysis API"]) # For backward compatibility with the prompt
app.include_router(ml_router, prefix="/api/risk", tags=["Risk Engine API"])
app.include_router(dashboard_router, prefix="/api", tags=["Dashboard Analytics"])
app.include_router(chat_router, prefix="/api", tags=["AI Chat Assistant"])
