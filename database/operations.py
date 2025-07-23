# database/operations.py
import pandas as pd
from datetime import datetime
from config.database import get_db_connection
from config.settings import DB_TYPE

def add_product(name, quantity, min_quantity, price, cost):
    """Add a new product to the database"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO products (name, quantity, min_quantity, price, cost, created_date, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, quantity, min_quantity, price, cost, current_time, current_time))
            
            conn.commit()
            return cursor.lastrowid
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                products_sheet = spreadsheet.worksheet('products')
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Get next ID
                existing_data = products_sheet.get_all_values()
                next_id = len(existing_data)  # Header row + data rows
                
                # Add new row
                products_sheet.append_row([
                    next_id, name, quantity, min_quantity, price, cost, current_time, current_time
                ])
                
                return next_id

def get_all_products():
    """Get all products from the database"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            df = pd.read_sql_query("SELECT * FROM products ORDER BY name", conn)
            
            # Ensure proper data types
            if not df.empty:
                df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
                df['min_quantity'] = pd.to_numeric(df['min_quantity'], errors='coerce').fillna(5).astype(int)
                df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0).astype(float)
                df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0).astype(float)
            
            return df
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    products_sheet = spreadsheet.worksheet('products')
                    data = products_sheet.get_all_records()
                    
                    if data:
                        df = pd.DataFrame(data)
                        # Ensure proper data types
                        df['product_id'] = pd.to_numeric(df['product_id'], errors='coerce').fillna(0).astype(int)
                        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0).astype(int)
                        df['min_quantity'] = pd.to_numeric(df['min_quantity'], errors='coerce').fillna(5).astype(int)
                        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0).astype(float)
                        df['cost'] = pd.to_numeric(df['cost'], errors='coerce').fillna(0.0).astype(float)
                        return df.sort_values('name')
                    else:
                        return pd.DataFrame()
                except:
                    return pd.DataFrame()
            return pd.DataFrame()

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            return cursor.fetchone()
    
    elif DB_TYPE == "sheets":
        df = get_all_products()
        if not df.empty:
            product = df[df['product_id'] == product_id]
            if not product.empty:
                return product.iloc[0].to_dict()
        return None

def delete_product(product_id):
    """Delete a product and its related transactions"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Delete related transactions first
            cursor.execute("DELETE FROM transactions WHERE product_id = ?", (product_id,))
            # Delete the product
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    products_sheet = spreadsheet.worksheet('products')
                    
                    # Find the row to delete
                    all_values = products_sheet.get_all_values()
                    for i, row in enumerate(all_values):
                        if i > 0 and row[0] == str(product_id):  # Skip header row
                            products_sheet.delete_rows(i + 1)
                            
                            # Also delete related transactions
                            try:
                                transactions_sheet = spreadsheet.worksheet('transactions')
                                trans_values = transactions_sheet.get_all_values()
                                rows_to_delete = []
                                for j, trans_row in enumerate(trans_values):
                                    if j > 0 and trans_row[1] == str(product_id):  # Skip header, check product_id
                                        rows_to_delete.append(j + 1)
                                
                                # Delete transaction rows (in reverse order to maintain indices)
                                for row_num in reversed(rows_to_delete):
                                    transactions_sheet.delete_rows(row_num)
                            except:
                                pass  # Transactions sheet might not exist yet
                            
                            return True
                    return False
                except:
                    return False

def search_products(search_term):
    """Search products by name"""
    df = get_all_products()
    if not df.empty:
        return df[df['name'].str.contains(search_term, case=False, na=False)]
    return df

def get_low_stock_products():
    """Get products that are at or below minimum quantity"""
    df = get_all_products()
    if not df.empty:
        return df[df['quantity'] <= df['min_quantity']]
    return df

def get_inventory_stats():
    """Get basic inventory statistics"""
    df = get_all_products()
    
    if df.empty:
        return {
            'total_products': 0,
            'total_value': 0,
            'total_items': 0,
            'low_stock_count': 0
        }
    
    return {
        'total_products': len(df),
        'total_value': (df['quantity'] * df['price']).sum(),
        'total_items': df['quantity'].sum(),
        'low_stock_count': len(df[df['quantity'] <= df['min_quantity']])
    }

def update_product_stock(product_id, new_quantity):
    """Update product stock quantity"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, last_updated = ?
                WHERE product_id = ?
            """, (int(new_quantity), current_time, product_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    products_sheet = spreadsheet.worksheet('products')
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Find and update the product
                    all_values = products_sheet.get_all_values()
                    for i, row in enumerate(all_values):
                        if i > 0 and row[0] == str(product_id):  # Skip header row
                            # Update quantity (column C = 3) and last_updated (column H = 8)
                            products_sheet.update_cell(i + 1, 3, new_quantity)
                            products_sheet.update_cell(i + 1, 8, current_time)
                            return True
                    return False
                except:
                    return False

def add_transaction(product_id, transaction_type, quantity_change):
    """Add a transaction record"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute("""
                INSERT INTO transactions (product_id, transaction_type, quantity_change, timestamp)
                VALUES (?, ?, ?, ?)
            """, (int(product_id), str(transaction_type), int(quantity_change), current_time))
            
            conn.commit()
            return cursor.lastrowid
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    transactions_sheet = spreadsheet.worksheet('transactions')
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Get next transaction ID
                    existing_data = transactions_sheet.get_all_values()
                    next_id = len(existing_data)  # Header row + data rows
                    
                    # Add new transaction
                    transactions_sheet.append_row([
                        next_id, product_id, transaction_type, quantity_change, current_time
                    ])
                    
                    return next_id
                except:
                    # Transactions sheet might not exist, create it
                    try:
                        transactions_sheet = spreadsheet.add_worksheet(title="transactions", rows="100", cols="5")
                        transactions_sheet.append_row(['transaction_id', 'product_id', 'transaction_type', 'quantity_change', 'timestamp'])
                        transactions_sheet.append_row([1, product_id, transaction_type, quantity_change, current_time])
                        return 1
                    except:
                        return None

def update_product_details(product_id, name, min_quantity, price, cost):
    """Update product details (name, price, etc.)"""
    if DB_TYPE == "sqlite":
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
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    products_sheet = spreadsheet.worksheet('products')
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Find and update the product
                    all_values = products_sheet.get_all_values()
                    for i, row in enumerate(all_values):
                        if i > 0 and row[0] == str(product_id):  # Skip header row
                            # Update: name(B=2), min_quantity(D=4), price(E=5), cost(F=6), last_updated(H=8)
                            products_sheet.update_cell(i + 1, 2, name)
                            products_sheet.update_cell(i + 1, 4, min_quantity)
                            products_sheet.update_cell(i + 1, 5, price)
                            products_sheet.update_cell(i + 1, 6, cost)
                            products_sheet.update_cell(i + 1, 8, current_time)
                            return True
                    return False
                except:
                    return False

def get_product_transactions(product_id):
    """Get all transactions for a specific product"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            query = """
                SELECT * FROM transactions 
                WHERE product_id = ? 
                ORDER BY timestamp DESC
            """
            df = pd.read_sql_query(query, conn, params=[product_id])
            return df
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    transactions_sheet = spreadsheet.worksheet('transactions')
                    data = transactions_sheet.get_all_records()
                    
                    if data:
                        df = pd.DataFrame(data)
                        df['product_id'] = pd.to_numeric(df['product_id'], errors='coerce')
                        filtered_df = df[df['product_id'] == product_id]
                        return filtered_df.sort_values('timestamp', ascending=False)
                    else:
                        return pd.DataFrame()
                except:
                    return pd.DataFrame()
            return pd.DataFrame()

def get_all_transactions():
    """Get all transactions with product names"""
    if DB_TYPE == "sqlite":
        with get_db_connection() as conn:
            query = """
                SELECT t.*, p.name as product_name
                FROM transactions t
                JOIN products p ON t.product_id = p.product_id
                ORDER BY t.timestamp DESC
            """
            df = pd.read_sql_query(query, conn)
            return df
    
    elif DB_TYPE == "sheets":
        with get_db_connection() as (gc, spreadsheet):
            if spreadsheet:
                try:
                    transactions_sheet = spreadsheet.worksheet('transactions')
                    products_df = get_all_products()
                    
                    trans_data = transactions_sheet.get_all_records()
                    
                    if trans_data and not products_df.empty:
                        trans_df = pd.DataFrame(trans_data)
                        trans_df['product_id'] = pd.to_numeric(trans_df['product_id'], errors='coerce')
                        
                        # Join with products to get names
                        merged_df = trans_df.merge(
                            products_df[['product_id', 'name']], 
                            on='product_id', 
                            how='left'
                        )
                        merged_df = merged_df.rename(columns={'name': 'product_name'})
                        return merged_df.sort_values('timestamp', ascending=False)
                    else:
                        return pd.DataFrame()
                except:
                    return pd.DataFrame()
            return pd.DataFrame()