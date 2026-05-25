from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Union
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    APP_NAME: str = "PoultryGuard AI API"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-this-in-production-use-a-real-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str = "sqlite:///./poultryguard.db"
    CORS_ORIGINS: Union[list[str], str] = [
        "http://localhost:3000",
        "https://poultrydesies.netlify.app",
    ]
    MAX_UPLOAD_MB: int = 5
    ALERT_CONFIDENCE_THRESHOLD: float = 0.70
    IMAGE_MODEL_PATH: str = "../AI/models/poultry_cnn.keras"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def check_sqlite_path(cls, value):
        if isinstance(value, str) and value.startswith("sqlite"):
            if os.environ.get("NETLIFY") == "true" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
                return "sqlite:////tmp/poultryguard.db"
        return value


settings = Settings()
