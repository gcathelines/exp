"""
Configuration management for the BI Chat CLI.
Loads settings from environment variables and config files.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


class Config(BaseModel):
    """Typed configuration for the BI Chat CLI."""

    # Google Cloud Configuration
    google_cloud_project: str
    google_application_credentials: str
    bigquery_dataset: str
    bigquery_table: str
    # VertexAI Configuration
    vertex_ai_project: str
    vertex_ai_location: str = "us-central1"
    vertex_ai_model: str = "gemini-2.0-flash"
    # Application Configuration
    log_level: str = "INFO"
    environment: str = "development"
    # Safety Configuration
    max_date_range_days: int = 30
    query_timeout_seconds: int = 300


def load_config(config_path: str | None = None) -> Config:
    """Load configuration from environment variables and config files."""
    # Load environment variables from .env file
    path = Path.cwd() / ".env" if not config_path else Path(config_path)

    if not path.exists():
        raise FileNotFoundError("Config file not found")
    load_dotenv(path)

    # Create config from environment variables - Pydantic will validate required fields
    config = Config(
        google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT", ""),
        google_application_credentials=os.getenv("GOOGLE_APPLICATION_CREDENTIALS", ""),
        bigquery_dataset=os.getenv("BIGQUERY_DATASET", ""),
        bigquery_table=os.getenv("BIGQUERY_TABLE", ""),
        vertex_ai_project=os.getenv("VERTEX_AI_PROJECT", ""),
        vertex_ai_location=os.getenv("VERTEX_AI_LOCATION", "us-central1"),
        vertex_ai_model=os.getenv("VERTEX_AI_MODEL", "gemini-2.0-flash"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        environment=os.getenv("ENVIRONMENT", "development"),
        max_date_range_days=int(os.getenv("MAX_DATE_RANGE_DAYS", "30")),
        query_timeout_seconds=int(os.getenv("QUERY_TIMEOUT_SECONDS", "300")),
    )

    # Validate credentials file exists
    cred_path = Path(config.google_application_credentials)
    if not cred_path.exists():
        raise FileNotFoundError(
            f"Service account file not found: {config.google_application_credentials}"
        )

    return config
