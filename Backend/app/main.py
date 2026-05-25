from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.extension import _rate_limit_exceeded_handler

from app.api.routes import auth, farms, records, predictions, alerts, dashboard, history, tts
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.APP_NAME)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS configuration
cors_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3003",
    "http://127.0.0.1:3004",
    "https://poultrydesies.netlify.app",
]

# Add configured CORS origins (production Netlify URLs etc.)
cors_origins.extend(settings.CORS_ORIGINS)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(farms.router, prefix="/api/farms", tags=["Farms"])
app.include_router(records.router, prefix="/api/records", tags=["Records"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(history.router, prefix="/api/history", tags=["History"])
app.include_router(tts.router, prefix="/api/tts", tags=["TTS"])


@app.get("/")
def root():
    return {
        "message": "PoultryGuard AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
def healthcheck():
    return {"status": "ok", "app": settings.APP_NAME}


@app.on_event("startup")
def on_startup():
    import os
    import shutil
    from pathlib import Path
    from app.db.session import engine
    from app.models.base import Base

    # 1. Initialize database tables
    Base.metadata.create_all(bind=engine)

    # 2. Copy reference images to /tmp if in serverless environment
    if os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        func_dir = Path(__file__).resolve().parent.parent
        src_dir = func_dir / "disease_references"
        dest_dir = Path("/tmp/disease_references")
        if src_dir.exists():
            try:
                shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
                print("Successfully copied preloaded disease references to /tmp/disease_references")
            except Exception as e:
                print(f"Error copying references: {e}")

