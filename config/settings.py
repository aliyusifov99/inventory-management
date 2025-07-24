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

# Supabase PostgreSQL settings
SUPABASE_CONFIG = {
    "host": os.getenv("SUPABASE_HOST"),
    "port": int(os.getenv("SUPABASE_PORT", "5432")),
    "database": os.getenv("SUPABASE_DATABASE", "postgres"),
    "user": os.getenv("SUPABASE_USER", "postgres"),
    "password": os.getenv("SUPABASE_PASSWORD"),
}

# App settings
APP_TITLE = "Anbar İdarəetmə Sistemi"
APP_ICON = "📦"
PAGE_LAYOUT = "wide"

# Create directories if they don't exist (for SQLite)
if DB_TYPE == "sqlite":
    DATA_DIR.mkdir(exist_ok=True)
    BACKUP_DIR.mkdir(exist_ok=True)

# Validate Supabase configuration when using PostgreSQL
if DB_TYPE == "postgres":
    required_vars = ["SUPABASE_HOST", "SUPABASE_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required Supabase environment variables: {', '.join(missing_vars)}")

# Check if running on Streamlit Cloud
IS_CLOUD_DEPLOYMENT = (
    os.getenv("STREAMLIT_SHARING_MODE") is not None or 
    os.getenv("HOSTNAME") == "streamlit" or
    "streamlit.app" in os.getenv("HOSTNAME", "")
)

print(f"🔧 Environment: {'☁️ Streamlit Cloud' if IS_CLOUD_DEPLOYMENT else '💻 Local'}")
print(f"🗄️ Database: {DB_TYPE.upper()}")
if DB_TYPE == "postgres":
    print(f"🐘 Supabase Host: {SUPABASE_CONFIG['host']}")