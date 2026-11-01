# ============================================================
# AGRIVISIONAI - CONFIGURATION
# Loads all sensitive keys and settings from environment variables.
# No secrets, passwords, or API keys are hardcoded here.
# ============================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Locate project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env in project root or current folder
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class Config:
    # --------------------------------------------------------
    # Flask Security
    # --------------------------------------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "agrivisionai-dev-secret-key-change-in-production")

    # --------------------------------------------------------
    # Database Configuration
    # --------------------------------------------------------
    # Fallback to local SQLite database if DATABASE_URL is not configured
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'agrivisionai.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --------------------------------------------------------
    # Weather API (OpenWeatherMap)
    # --------------------------------------------------------
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
    OPENWEATHER_BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL",
        "https://api.openweathermap.org/data/2.5"
    )

    # --------------------------------------------------------
    # Market Prices API (CEDA)
    # --------------------------------------------------------
    CEDA_API_KEY = os.getenv("CEDA_API_KEY", "")
    CEDA_BASE_URL = os.getenv(
        "CEDA_BASE_URL",
        "https://api.ceda.ashoka.edu.in/v1"
    )

    # --------------------------------------------------------
    # Email Service (Flask-Mail)
    # --------------------------------------------------------
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").strip().lower() in ("true", "1", "t", "yes")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").strip().lower() in ("true", "1", "t", "yes")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        os.getenv("MAIL_USERNAME", "")
    )
