"""
Configuration Management
Loads environment variables and application settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application Settings"""
    
    # App Settings
    APP_NAME: str = "Sistema Estoque 5S"
    DEBUG: bool = True
    
    # Database
    DATABASE_PATH: str = Field(default="data/estoque.db")
    
    # Google Sheets
    GOOGLE_SHEETS_SPREADSHEET_ID: str = Field(default="")
    GOOGLE_SHEETS_CREDENTIALS_FILE: str = Field(default="credentials/google_sheets_key.json")
    
    # Slack
    SLACK_BOT_TOKEN: str = Field(default="")
    SLACK_CHANNEL: str = Field(default="C09DV1KQS4C")
    SLACK_ENABLED: bool = Field(default=True)
    
    # Sync Settings
    SYNC_INTERVAL_MINUTES: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Ensure data directory exists
data_dir = Path(settings.DATABASE_PATH).parent
data_dir.mkdir(parents=True, exist_ok=True)

# Ensure credentials directory exists
cred_dir = Path(settings.GOOGLE_SHEETS_CREDENTIALS_FILE).parent
cred_dir.mkdir(parents=True, exist_ok=True)

