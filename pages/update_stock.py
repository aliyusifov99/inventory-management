# pages/update_stock.py
import streamlit as st
from datetime import datetime
from database.operations import (
    get_all_products, 
    get_product_by_id,
    update_product_stock,
    add_transaction,
    get_product_transactions
)
from utils.validation import format_currency

def show_update_stock_page():
    """Display the update stock page"""
    st.header("📈 Update Stock")
    
    # Get all products
    products_df = get_all_products()
    
    if products_df.empty:
        st.info("No products found. Add some products first to update stock.")
        return
    
    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["📦 Stock In/Out", "✏️ Edit Product", "📋 Transaction History"])
    
    with tab1:
        show_stock_update_tab(products_df)
    
    with tab2:
        show_edit_product_tab(products_df)
    
    with tab3:
        show_transaction_history_tab(products_df)

def show_stock_update_tab(products_df):
    """Tab for updating stock quantities"""
    st.subheader("Update Stock Quantity")
    
    # Product selection
    product_options = {
        row['product_id']: f"{row['name']} (Current: {int(row['quantity'])}) - {format_currency(float(row['price']))}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Select Product",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        help="Choose the product to update stock for"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        # Show current product info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Stock", int(selected_product['quantity']))
        with col2:
            st.metric("Minimum Level", int(selected_product['min_quantity']))
        with col3:
            st.metric("Price", format_currency(float(selected_product['price'])))
        
        # Stock update form
        with st.form("update_stock_form"):
            st.subheader("Stock Movement")
            
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox(
                    "Transaction Type",
                    ["SALE", "RESTOCK"],
                    help="SALE: Reduces stock, RESTOCK: Increases stock"
                )
            
            with col2:
                quantity_change = st.number_input(
                    "Quantity",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Amount to add or subtract from stock"
                )
            
            # Show preview of change
            current_stock = int(selected_product['quantity'])
            if transaction_type == "SALE":
                new_stock = current_stock - quantity_change
                change_text = f"Stock will decrease: {current_stock} → {new_stock}"
                if new_stock < 0:
                    st.error(f"⚠️ Not enough stock! Current: {current_stock}, Trying to sell: {quantity_change}")
            else:  # RESTOCK
                new_stock = current_stock + quantity_change
                change_text = f"Stock will increase: {current_stock} → {new_stock}"
            
            st.info(change_text)
            
            # Low stock warning
            if new_stock <= int(selected_product['min_quantity']):
                st.warning(f"⚠️ Stock will be at or below minimum level ({int(selected_product['min_quantity'])})")
            
            submitted = st.form_submit_button("Update Stock", type="primary")
            
            if submitted:
                if transaction_type == "SALE" and quantity_change > current_stock:
                    st.error("❌ Cannot sell more items than available in stock!")
                else:
                    try:
                        # Calculate new quantity
                        if transaction_type == "SALE":
                            new_quantity = current_stock - quantity_change
                            quantity_change_db = -quantity_change  # Negative for sales
                        else:  # RESTOCK
                            new_quantity = current_stock + quantity_change
                            quantity_change_db = quantity_change  # Positive for restock
                        
                        # Update stock and add transaction
                        update_product_stock(selected_product_id, new_quantity)
                        add_transaction(selected_product_id, transaction_type, quantity_change_db)
                        
                        st.success(f"✅ Stock updated successfully!")
                        st.success(f"📊 {selected_product['name']}: {current_stock} → {new_quantity}")
                        
                        # Show updated info automatically
                        st.info("🔄 Refresh the page to see updated stock levels.")
                        
                    except Exception as e:
                        st.error(f"❌ Error updating stock: {str(e)}")

def show_edit_product_tab(products_df):
    """Tab for editing product details"""
    st.subheader("Edit Product Details")
    
    # Product selection
    product_options = {
        row['product_id']: f"{row['name']} - {format_currency(row['price'])}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Select Product to Edit",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        key="edit_product_select"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        # Edit form
        with st.form("edit_product_form"):
            st.subheader(f"Editing: {selected_product['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Product Name", 
                    value=selected_product['name'],
                    help="Update product name"
                )
                new_min_quantity = st.number_input(
                    "Minimum Quantity", 
                    min_value=0, 
                    value=int(selected_product['min_quantity']),
                    step=1,
                    help="Update reorder level"
                )
            
            with col2:
                new_price = st.number_input(
                    "Selling Price", 
                    min_value=0.0, 
                    value=float(selected_product['price']),
                    step=0.01,
                    format="%.2f",
                    help="Update selling price"
                )
                new_cost = st.number_input(
                    "Purchase Cost", 
                    min_value=0.0, 
                    value=float(selected_product['cost']),
                    step=0.01,
                    format="%.2f",
                    help="Update purchase cost"
                )
            
            st.info("ℹ️ Note: This will not change the current stock quantity. Use 'Stock In/Out' tab to update quantities.")
            
            submitted = st.form_submit_button("Update Product", type="primary")
            
            if submitted:
                if not new_name or new_name.strip() == "":
                    st.error("❌ Product name cannot be empty!")
                elif new_price <= 0:
                    st.error("❌ Price must be greater than 0!")
                else:
                    try:
                        from database.operations import update_product_details
                        update_product_details(
                            selected_product_id,
                            new_name.strip(),
                            new_min_quantity,
                            new_price,
                            new_cost
                        )
                        st.success(f"✅ Product '{new_name.strip()}' updated successfully!")
                        st.info("🔄 Refresh the page to see updated details.")
                        
                    except Exception as e:
                        st.error(f"❌ Error updating product: {str(e)}")

def show_transaction_history_tab(products_df):
    """Tab for viewing transaction history"""
    st.subheader("Transaction History")
    
    # Product selection
    product_options = {
        row['product_id']: f"{row['name']}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Select Product to View History",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        key="history_product_select"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        st.subheader(f"History: {selected_product['name']}")
        
        # Get transactions
        transactions_df = get_product_transactions(selected_product_id)
        
        if transactions_df.empty:
            st.info("No transactions found for this product.")
        else:
            # Display summary
            col1, col2, col3 = st.columns(3)
            
            sales_count = len(transactions_df[transactions_df['transaction_type'] == 'SALE'])
            restock_count = len(transactions_df[transactions_df['transaction_type'] == 'RESTOCK'])
            total_sold = abs(transactions_df[transactions_df['transaction_type'] == 'SALE']['quantity_change'].sum())
            
            with col1:
                st.metric("Total Sales", sales_count)
            with col2:
                st.metric("Total Restocks", restock_count)
            with col3:
                st.metric("Items Sold", int(total_sold))
            
            # Display transactions table
            st.subheader("Recent Transactions")
            
            # Format the dataframe for display
            display_df = transactions_df.copy()
            display_df['Date'] = display_df['timestamp']
            display_df['Type'] = display_df['transaction_type']
            display_df['Change'] = display_df['quantity_change'].apply(
                lambda x: f"+{x}" if x > 0 else str(x)
            )
            
            # Select columns for display
            display_df = display_df[['Date', 'Type', 'Change']].sort_values('Date', ascending=False)
            
            st.dataframe(
                display_df, 
                use_container_width=True,
                column_config={
                    "Date": st.column_config.DatetimeColumn("Date & Time", width="large"),
                    "Type": st.column_config.TextColumn("Type", width="medium"),
                    "Change": st.column_config.TextColumn("Quantity Change", width="small")
                }
            )

if __name__ == "__main__":
    show_update_stock_page()