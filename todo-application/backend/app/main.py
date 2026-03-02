"""FastAPI application entry point."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from app.config import settings
from app.routers import auth, tasks
import logging
import asyncio

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A full-stack todo application with user authentication",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.ENVIRONMENT == "production" else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


# Note: SQLAlchemyError handler removed to allow route-specific error handling
# Each route should handle database errors appropriately for their use case



@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions."""
    import traceback
    error_traceback = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}\n{error_traceback}")

    # Always expose errors in development for debugging
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": f"{type(exc).__name__}: {str(exc)}",
            "traceback": error_traceback if settings.ENVIRONMENT == "development" else None
        }
    )


async def _keep_db_alive():
    """Ping Neon every 4 min so it never suspends (free tier suspends after 5 min idle)."""
    from app.database import engine
    while True:
        await asyncio.sleep(240)  # 4 minutes
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.debug("DB keep-alive ping OK")
        except Exception as e:
            logger.warning(f"DB keep-alive ping failed: {e}")


@app.on_event("startup")
async def startup():
    asyncio.create_task(_keep_db_alive())
    logger.info("DB keep-alive task started")


@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "message": "Todo API is running",
        "version": settings.VERSION,
        "docs": f"{settings.API_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }


# Register routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks.router, prefix=settings.API_PREFIX, tags=["Tasks"])
