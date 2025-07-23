# database/operations.py
import pandas as pd
from datetime import datetime
from config.database import get_db_connection

def add_product(name, quantity, min_quantity, price, cost):
    """Add a new product to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO products (name, quantity, min_quantity, price, cost, created_date, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, quantity, min_quantity, price, cost, current_time, current_time))
        
        conn.commit()
        return cursor.lastrowid

def get_all_products():
    """Get all products from the database"""
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM products ORDER BY name", conn)
        return df

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        return cursor.fetchone()

def delete_product(product_id):
    """Delete a product and its related transactions"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Delete related transactions first
        cursor.execute("DELETE FROM transactions WHERE product_id = ?", (product_id,))
        # Delete the product
        cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        
        conn.commit()
        return cursor.rowcount > 0

def search_products(search_term):
    """Search products by name"""
    with get_db_connection() as conn:
        query = "SELECT * FROM products WHERE name LIKE ? ORDER BY name"
        df = pd.read_sql_query(query, conn, params=[f"%{search_term}%"])
        return df

def get_low_stock_products():
    """Get products that are at or below minimum quantity"""
    with get_db_connection() as conn:
        query = "SELECT * FROM products WHERE quantity <= min_quantity ORDER BY name"
        df = pd.read_sql_query(query, conn)
        return df

def get_inventory_stats():
    """Get basic inventory statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        # Total stock value
        cursor.execute("SELECT SUM(quantity * price) FROM products")
        total_value = cursor.fetchone()[0] or 0
        
        # Total items
        cursor.execute("SELECT SUM(quantity) FROM products")
        total_items = cursor.fetchone()[0] or 0
        
        # Low stock count
        cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_quantity")
        low_stock_count = cursor.fetchone()[0]
        
        return {
            'total_products': total_products,
            'total_value': total_value,
            'total_items': total_items,
            'low_stock_count': low_stock_count
        }

def update_product_stock(product_id, new_quantity):
    """Update product stock quantity"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE products 
            SET quantity = ?, last_updated = ?
            WHERE product_id = ?
        """, (new_quantity, current_time, product_id))
        
        conn.commit()
        return cursor.rowcount > 0

def add_transaction(product_id, transaction_type, quantity_change):
    """Add a transaction record"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO transactions (product_id, transaction_type, quantity_change, timestamp)
            VALUES (?, ?, ?, ?)
        """, (product_id, transaction_type, quantity_change, current_time))
        
        conn.commit()
        return cursor.lastrowid

def update_product_details(product_id, name, min_quantity, price, cost):
    """Update product details (name, price, etc.)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE products 
            SET name = ?, min_quantity = ?, price = ?, cost = ?, last_updated = ?
            WHERE product_id = ?
        """, (name, min_quantity, price, cost, current_time, product_id))
        
        conn.commit()
        return cursor.rowcount > 0

def get_product_transactions(product_id):
    """Get all transactions for a specific product"""
    with get_db_connection() as conn:
        query = """
            SELECT * FROM transactions 
            WHERE product_id = ? 
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, conn, params=[product_id])
        return df

def get_all_transactions():
    """Get all transactions with product names"""
    with get_db_connection() as conn:
        query = """
            SELECT t.*, p.name as product_name
            FROM transactions t
            JOIN products p ON t.product_id = p.product_id
            ORDER BY t.timestamp DESC
        """
        df = pd.read_sql_query(query, conn)
        return df