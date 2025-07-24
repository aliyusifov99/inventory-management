# database/operations.py
import pandas as pd
from datetime import datetime
from config.database import get_db_connection, get_sqlalchemy_engine
from config.settings import DB_TYPE

def add_product(name, quantity, min_quantity, price, cost):
    """Add a new product to the database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if DB_TYPE == "postgres":
            cursor.execute('''
                INSERT INTO products (name, quantity, min_quantity, price, cost, created_date, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (name, quantity, min_quantity, price, cost, current_time, current_time))
        else:  # sqlite
            cursor.execute('''
                INSERT INTO products (name, quantity, min_quantity, price, cost, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, quantity, min_quantity, price, cost, current_time, current_time))
        
        conn.commit()
        return cursor.lastrowid if DB_TYPE == "sqlite" else cursor.rowcount

def get_all_products():
    """Get all products from the database"""
    engine = get_sqlalchemy_engine()
    df = pd.read_sql_query("SELECT * FROM products ORDER BY name", engine)
    
    # Ensure proper data types
    if not df.empty:
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
        df['min_quantity'] = pd.to_numeric(df['min_quantity'], errors='coerce').fillna(5).astype(int)
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0).astype(float)
        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0).astype(float)
    
    return df

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if DB_TYPE == "postgres":
            cursor.execute("SELECT * FROM products WHERE product_id = %s", (product_id,))
        else:  # sqlite
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        
        return cursor.fetchone()

def delete_product(product_id):
    """Delete a product and its related transactions"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if DB_TYPE == "postgres":
            # Delete related transactions first
            cursor.execute("DELETE FROM transactions WHERE product_id = %s", (product_id,))
            # Delete the product
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        else:  # sqlite
            # Delete related transactions first
            cursor.execute("DELETE FROM transactions WHERE product_id = ?", (product_id,))
            # Delete the product
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
        
        conn.commit()
        return cursor.rowcount > 0

def search_products(search_term):
    """Search products by name"""
    engine = get_sqlalchemy_engine()
    
    if DB_TYPE == "postgres":
        # Use text() for raw SQL with named parameters
        from sqlalchemy import text
        query = text("SELECT * FROM products WHERE name ILIKE :search_term ORDER BY name")
        df = pd.read_sql_query(query, engine, params={"search_term": f"%{search_term}%"})
    else:  # sqlite
        query = "SELECT * FROM products WHERE name LIKE ? ORDER BY name"
        df = pd.read_sql_query(query, engine, params=[f"%{search_term}%"])
    
    return df

def get_low_stock_products():
    """Get products that are at or below minimum quantity"""
    engine = get_sqlalchemy_engine()
    query = "SELECT * FROM products WHERE quantity <= min_quantity ORDER BY name"
    df = pd.read_sql_query(query, engine)
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
            'total_value': float(total_value),
            'total_items': int(total_items),
            'low_stock_count': low_stock_count
        }

def update_product_stock(product_id, new_quantity):
    """Update product stock quantity"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if DB_TYPE == "postgres":
            cursor.execute("""
                UPDATE products 
                SET quantity = %s, last_updated = %s
                WHERE product_id = %s
            """, (int(new_quantity), current_time, product_id))
        else:  # sqlite
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, last_updated = ?
                WHERE product_id = ?
            """, (int(new_quantity), current_time, product_id))
        
        conn.commit()
        return cursor.rowcount > 0

def add_transaction(product_id, transaction_type, quantity_change):
    """Add a transaction record"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if DB_TYPE == "postgres":
            cursor.execute("""
                INSERT INTO transactions (product_id, transaction_type, quantity_change, timestamp)
                VALUES (%s, %s, %s, %s)
            """, (int(product_id), str(transaction_type), int(quantity_change), current_time))
        else:  # sqlite
            cursor.execute("""
                INSERT INTO transactions (product_id, transaction_type, quantity_change, timestamp)
                VALUES (?, ?, ?, ?)
            """, (int(product_id), str(transaction_type), int(quantity_change), current_time))
        
        conn.commit()
        return cursor.lastrowid if DB_TYPE == "sqlite" else cursor.rowcount

def update_product_details(product_id, name, min_quantity, price, cost):
    """Update product details (name, price, etc.)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if DB_TYPE == "postgres":
            cursor.execute("""
                UPDATE products 
                SET name = %s, min_quantity = %s, price = %s, cost = %s, last_updated = %s
                WHERE product_id = %s
            """, (name, min_quantity, price, cost, current_time, product_id))
        else:  # sqlite
            cursor.execute("""
                UPDATE products 
                SET name = ?, min_quantity = ?, price = ?, cost = ?, last_updated = ?
                WHERE product_id = ?
            """, (name, min_quantity, price, cost, current_time, product_id))
        
        conn.commit()
        return cursor.rowcount > 0

def get_product_transactions(product_id):
    """Get all transactions for a specific product"""
    engine = get_sqlalchemy_engine()
    
    if DB_TYPE == "postgres":
        from sqlalchemy import text
        query = text("""
            SELECT * FROM transactions 
            WHERE product_id = :product_id 
            ORDER BY timestamp DESC
        """)
        df = pd.read_sql_query(query, engine, params={"product_id": product_id})
    else:  # sqlite
        query = """
            SELECT * FROM transactions 
            WHERE product_id = ? 
            ORDER BY timestamp DESC
        """
        df = pd.read_sql_query(query, engine, params=[product_id])
    
    return df

def get_all_transactions():
    """Get all transactions with product names"""
    engine = get_sqlalchemy_engine()
    query = """
        SELECT t.*, p.name as product_name
        FROM transactions t
        JOIN products p ON t.product_id = p.product_id
        ORDER BY t.timestamp DESC
    """
    df = pd.read_sql_query(query, engine)
    return df