import os
import sys
from pathlib import Path

# Add function directory to python path
func_dir = Path(__file__).resolve().parent
sys.path.append(str(func_dir))

from mangum import Mangum
from app.main import app

# Create the standard mangum handler
mangum_handler = Mangum(app)


def _normalize_api_path(value: str) -> str:
    """Normalize Netlify function paths to FastAPI's expected /api/* shape."""
    prefix = "/.netlify/functions/api"
    if not value.startswith(prefix):
        return value

    stripped = value[len(prefix):]
    if not stripped:
        return "/"

    if stripped.startswith("/api/") or stripped == "/api":
        return stripped

    if stripped.startswith("/"):
        return f"/api{stripped}"

    return f"/api/{stripped}"


def handler(event, context):
    # Netlify can forward either /api/* or /.netlify/functions/api/* paths.
    if "path" in event and isinstance(event["path"], str):
        event["path"] = _normalize_api_path(event["path"])

    if "rawPath" in event and isinstance(event["rawPath"], str):
        event["rawPath"] = _normalize_api_path(event["rawPath"])

    return mangum_handler(event, context)
