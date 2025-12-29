import os
import sys
from contextlib import asynccontextmanager
from typing import List

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from plana.api.middleware.auth import AuthMiddleware
from plana.api.routes import auth, messages, users
from plana.api.routes.guilds import GUILD_ROUTER
from plana.api.utils.helper import validate_environment


def setup_logging(debug: bool = False) -> None:
    """Configure logging for the application"""
    logger.remove()  # Remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not debug else "DEBUG",
        colorize=True,
    )
    logger.add(
        "logs/api.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
    )


def get_cors_origins() -> List[str]:
    """Get CORS origins from environment with validation"""
    origins_str = os.getenv("ALLOWED_ORIGINS", "http://127.0.0.1:8080")
    origins = [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    logger.info(f"CORS origins configured: {origins}")
    return origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting Plana Discord Bot API...")

    try:
        from plana.database import PlanaDB
        from plana.database.utils.db import get_database_url

        validate_environment()

        # Initialize database
        connection_string = get_database_url()
        logger.info("Initializing database connection...")
        PlanaDB.init_db(connection_string=connection_string)
        logger.success("Database initialized successfully")

        # Create tables if they don't exist
        await PlanaDB.create_all()
        logger.success("Database tables ready")

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        sys.exit(1)

    yield

    # Shutdown
    logger.info("Shutting down Plana Discord Bot API...")
    logger.success("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Plana Discord Bot API",
        description="Advanced Discord bot management API with OAuth 2.0 authentication",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS middleware
    try:
        origins = get_cors_origins()
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
    except Exception as e:
        logger.error(f"Failed to configure CORS: {e}")
        raise

    # Add authentication middleware
    app.add_middleware(AuthMiddleware)

    # Include routers
    app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
    app.include_router(GUILD_ROUTER, prefix="/api/guilds", tags=["Guilds Management"])
    app.include_router(
        messages.MESSAGE_ROUTER,
        prefix="/api/messages",
        tags=["Internal Messages Management"],
    )
    app.include_router(users.USER_ROUTER, prefix="/api/users", tags=["User Management"])

    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle validation errors"""
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        logger.warning(
            f"HTTP error on {request.url.path}: {exc.status_code} - {exc.detail}"
        )
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )

    return app


# Create the app instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Plana Discord Bot API is running!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp in production
    }


def main():
    """Main entry point for the server"""
    try:

        # Server configuration
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", 8000))
        debug_mode = bool(os.getenv("DEBUG", False))

        # Setup logging
        setup_logging(debug_mode)
        # Load environment variables
        validate_environment()

        logger.info(f"Starting Plana Discord Bot API on {host}:{port}")

        # Start the server
        uvicorn.run(
            "plana.api.main:app",
            host=host,
            port=port,
            log_level="info",
            reload=debug_mode,
        )

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
