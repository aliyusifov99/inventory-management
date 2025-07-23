# config/database.py
import sqlite3
import contextlib
import streamlit as st
from config.settings import DB_PATH, IS_CLOUD_DEPLOYMENT

def get_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

@contextlib.contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the SQLite database and create tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create products table
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
        
        # Create transactions table
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

def test_connection():
    """Test database connection"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        if not IS_CLOUD_DEPLOYMENT:
            st.error(f"❌ Database connection test failed: {str(e)}")
        return False