import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str
    
    # Validation constraints
    COUNTRY_CODE: str = "CO"
    MAX_HOURS_PER_DAY: int = 8
    MAX_HOURS_PER_DAY: int = 8
    MAX_TASKS_PER_DAY: int = 5
    DEFAULT_CLIENT_PROJECT: str = "Synaptica"
    
    # Target Year
    HOLIDAYS_YEAR: int = 2026
    
    # Repositories to scan (can be paths or URLs if using remote fetcher)
    REPO_LIST: List[str] = [
        r"C:\Users\esteb\Desktop\REPOS-SYNAPTICA\auto-report"
    ]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
