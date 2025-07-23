# config/database.py
import sqlite3
import gspread
import pandas as pd
import contextlib
import streamlit as st
from datetime import datetime
from google.auth import default
from config.settings import DB_TYPE, DB_PATH, GOOGLE_SHEETS_URL, IS_CLOUD_DEPLOYMENT

# Global variable to store Google Sheets client
_sheets_client = None
_spreadsheet = None

def get_sheets_client():
    """Get Google Sheets client with authentication"""
    global _sheets_client, _spreadsheet
    
    if _sheets_client is None:
        try:
            # Try to use default credentials (works on Streamlit Cloud)
            gc = gspread.service_account()
        except:
            try:
                # Fallback to anonymous access for public sheets
                gc = gspread.Client()
            except Exception as e:
                st.error(f"❌ Could not connect to Google Sheets: {str(e)}")
                return None, None
        
        _sheets_client = gc
    
    if _spreadsheet is None:
        try:
            _spreadsheet = _sheets_client.open_by_url(GOOGLE_SHEETS_URL)
        except Exception as e:
            st.error(f"❌ Could not open spreadsheet: {str(e)}")
            st.info("💡 Make sure the Google Sheets URL is correct and publicly accessible")
            return None, None
    
    return _sheets_client, _spreadsheet

def get_connection():
    """Get database connection based on configuration"""
    if DB_TYPE == "sqlite":
        return sqlite3.connect(str(DB_PATH), check_same_thread=False)
    elif DB_TYPE == "sheets":
        return get_sheets_client()
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

@contextlib.contextmanager
def get_db_connection():
    """Context manager for database connections"""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        try:
            yield conn
        finally:
            conn.close()
    elif DB_TYPE == "sheets":
        gc, spreadsheet = get_sheets_client()
        yield (gc, spreadsheet)

def init_database():
    """Initialize the database and create tables"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    min_quantity INTEGER NOT NULL DEFAULT 0,
                    price REAL NOT NULL DEFAULT 0.0,
                    cost REAL NOT NULL DEFAULT 0.0,
                    created_date TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    transaction_type TEXT NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (product_id)
                )
            ''')
            
            conn.commit()
    
    elif DB_TYPE == "sheets":
        # Google Sheets are already set up manually
        # Just verify they exist
        try:
            with get_db_connection() as (gc, spreadsheet):
                if spreadsheet:
                    worksheets = [ws.title for ws in spreadsheet.worksheets()]
                    required_sheets = ['products', 'transactions']
                    
                    for sheet_name in required_sheets:
                        if sheet_name not in worksheets:
                            st.error(f"❌ Missing '{sheet_name}' sheet in Google Sheets")
                            return False
                    return True
        except Exception as e:
            if not IS_CLOUD_DEPLOYMENT:
                st.error(f"❌ Could not verify Google Sheets: {str(e)}")
            return False

def test_connection():
    """Test database connection"""
    try:
        if DB_TYPE == "sqlite":
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        
        elif DB_TYPE == "sheets":
            with get_db_connection() as (gc, spreadsheet):
                if spreadsheet:
                    # Try to read first cell
                    products_sheet = spreadsheet.worksheet('products')
                    products_sheet.cell(1, 1).value
                    return True
                return False
                
    except Exception as e:
        if not IS_CLOUD_DEPLOYMENT:
            st.error(f"❌ Database connection test failed: {str(e)}")
        return False