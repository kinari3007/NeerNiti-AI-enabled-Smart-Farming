"""
Application configuration loaded from environment variables or .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import ClassVar


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "NeerNiti Smart Farming API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database — defaults to local SQLite for development
    # For PostgreSQL: postgresql+asyncpg://user:password@host:5432/dbname
    DATABASE_URL: str = "sqlite+aiosqlite:///./neerniti.db"

    # Weather (Open-Meteo — free, no API key required)
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1/forecast"
    WEATHER_CACHE_TTL_SECONDS: int = 1800  # 30 minutes

    # Admin API key — protects POST /fertilizers and price import endpoints
    # MUST be changed in production via environment variable
    ADMIN_API_KEY: str = "change-me-in-production"

    # CORS — frontend dev servers
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # ML model paths (relative to repo root, resolved at runtime)
    ML_MODEL_PATH: str = "ml/artifacts/fertilizer_classifier.pkl"
    ML_LABEL_ENCODER_PATH: str = "ml/artifacts/label_encoder.pkl"
    ML_SCALER_PATH: str = "ml/artifacts/feature_scaler.pkl"
    ML_MODEL_VERSION: str = "1.0.0"

    # Soil validation ranges — scientifically justified bounds
    # Values outside these ranges are flagged, NOT rejected
    SOIL_PH_MIN: float = 0.0
    SOIL_PH_MAX: float = 14.0
    SOIL_PH_AGRONOMIC_MIN: float = 4.0   # below this is flagged as atypical
    SOIL_PH_AGRONOMIC_MAX: float = 8.5   # above this is flagged as atypical
    SOIL_EC_MIN: float = 0.0
    SOIL_EC_MAX: float = 20.0            # dS/m
    SOIL_EC_HIGH_THRESHOLD: float = 4.0  # above this flags salinity concern
    SOIL_MOISTURE_MIN: float = 0.0
    SOIL_MOISTURE_MAX: float = 100.0     # percentage
    SOIL_NPK_MAX: float = 10000.0        # mg/kg upper sanity bound
    SOIL_N_HIGH_THRESHOLD: float = 500.0 # mg/kg — unusually high nitrogen


def get_settings() -> "Settings":
    return Settings()


settings = get_settings()
