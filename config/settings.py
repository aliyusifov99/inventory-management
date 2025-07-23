# config/settings.py
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available in cloud deployment

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"

# Database settings
DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()

# SQLite settings (for local development)
DB_NAME = "inventory.db"
DB_PATH = DATA_DIR / DB_NAME

# Google Sheets settings
GOOGLE_SHEETS_URL = os.getenv("GOOGLE_SHEETS_URL")

# App settings
APP_TITLE = "Inventory Management System"
APP_ICON = "📦"
PAGE_LAYOUT = "wide"

# Create directories if they don't exist (for SQLite)
if DB_TYPE == "sqlite":
    DATA_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

# Validate Google Sheets configuration
if DB_TYPE == "sheets":
    if not GOOGLE_SHEETS_URL:
        raise ValueError("Missing GOOGLE_SHEETS_URL environment variable")

# Check if running on Streamlit Cloud
IS_CLOUD_DEPLOYMENT = (
    os.getenv("STREAMLIT_SHARING_MODE") is not None or 
    os.getenv("HOSTNAME") == "streamlit" or
    "streamlit.app" in os.getenv("HOSTNAME", "")
)

print(f"🔧 Environment: {'☁️ Streamlit Cloud' if IS_CLOUD_DEPLOYMENT else '💻 Local'}")
print(f"🗄️ Database: {DB_TYPE.upper()}")
if DB_TYPE == "sheets":
    print(f"📊 Google Sheets: {GOOGLE_SHEETS_URL[:50]}...")