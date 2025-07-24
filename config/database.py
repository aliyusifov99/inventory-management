# config/database.py
import sqlite3
import psycopg2
import contextlib
import streamlit as st
from sqlalchemy import create_engine
from config.settings import DB_TYPE, DB_PATH, SUPABASE_CONFIG, IS_CLOUD_DEPLOYMENT

def get_connection():
    """Get database connection based on configuration"""
    if DB_TYPE == "sqlite":
        return sqlite3.connect(str(DB_PATH), check_same_thread=False)
    elif DB_TYPE == "postgres":
        try:
            return psycopg2.connect(**SUPABASE_CONFIG)
        except Exception as e:
            if not IS_CLOUD_DEPLOYMENT:
                st.error(f"❌ Failed to connect to Supabase: {str(e)}")
                st.info("💡 Check your .env file with Supabase credentials")
            raise e
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

def get_sqlalchemy_engine():
    """Get SQLAlchemy engine for pandas operations"""
    if DB_TYPE == "sqlite":
        return create_engine(f"sqlite:///{DB_PATH}")
    elif DB_TYPE == "postgres":
        config = SUPABASE_CONFIG
        connection_string = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        return create_engine(connection_string)
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

@contextlib.contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database and create tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if DB_TYPE == "sqlite":
            # SQLite table creation
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
        
        elif DB_TYPE == "postgres":
            # PostgreSQL table creation with better error handling
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 0,
                    min_quantity INTEGER NOT NULL DEFAULT 0,
                    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
                    created_date TIMESTAMP NOT NULL,
                    last_updated TIMESTAMP NOT NULL
                )
            ''')
            
            # Create indexes only if they don't exist
            try:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_products_name ON products (name)
                ''')
            except:
                pass  # Index might already exist
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id SERIAL PRIMARY KEY,
                    product_id INTEGER NOT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    quantity_change INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes only if they don't exist
            try:
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions (product_id)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions (timestamp)
                ''')
            except:
                pass  # Indexes might already exist
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