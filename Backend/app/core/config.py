from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Union


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    APP_NAME: str = "PoultryGuard AI API"
    APP_ENV: str = "development"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    DATABASE_URL: str
    CORS_ORIGINS: Union[list[str], str] = ["http://localhost:3000"]
    MAX_UPLOAD_MB: int = 5
    ALERT_CONFIDENCE_THRESHOLD: float = 0.70
    IMAGE_MODEL_PATH: str = "../AI/models/poultry_cnn.keras"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, value):
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
