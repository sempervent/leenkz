"""Main FastAPI application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from leenkz.core.config import settings, get_static_dir
from leenkz.core.database import engine
from leenkz.api.routers import auth, links, tags, shares, snapshots, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    
    # Create static directory if it doesn't exist
    static_dir = get_static_dir()
    static_dir.mkdir(exist_ok=True)
    
    yield
    
    # Shutdown
    await engine.dispose()
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Keep your links tagged and stored available on any device",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(links.router, prefix="/api/links", tags=["links"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(shares.router, prefix="/api/shares", tags=["shares"])
app.include_router(snapshots.router, prefix="/api", tags=["snapshots"])
app.include_router(users.router, prefix="/api/users", tags=["users"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint for Docker."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }


# Mount static files for React SPA
static_dir = get_static_dir()
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
else:
    # Fallback for development
    @app.get("/")
    async def root():
        return {"message": "Leenkz API is running. Build the frontend to see the SPA."}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "leenkz.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    ) 