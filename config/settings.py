# config/settings.py
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUP_DIR = PROJECT_ROOT / "backups"

# Database settings (SQLite only for cloud deployment)
DB_NAME = "inventory.db"
DB_PATH = DATA_DIR / DB_NAME

# App settings
APP_TITLE = "Inventory Management System"
APP_ICON = "📦"
PAGE_LAYOUT = "wide"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# For Streamlit Cloud deployment
IS_CLOUD_DEPLOYMENT = os.getenv("STREAMLIT_SHARING_MODE") is not None or os.getenv("HOSTNAME") == "streamlit"

print(f"🔧 Running on: {'☁️ Streamlit Cloud' if IS_CLOUD_DEPLOYMENT else '💻 Local Environment'}")
print(f"🗄️ Database: SQLite")