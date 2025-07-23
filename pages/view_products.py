# pages/view_products.py
import streamlit as st
from database.operations import (
    get_all_products, 
    delete_product, 
    search_products, 
    get_inventory_stats,
    get_low_stock_products
)
from utils.validation import format_currency

def show_view_products_page():
    """Display the view products page"""
    st.header("All Products")
    
    # Get inventory statistics
    stats = get_inventory_stats()
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", stats['total_products'])
    
    with col2:
        st.metric("Total Stock Value", format_currency(stats['total_value']))
    
    with col3:
        st.metric("Low Stock Items", stats['low_stock_count'])
    
    with col4:
        st.metric("Total Items", stats['total_items'])
    
    # Low stock alerts
    low_stock_items = get_low_stock_products()
    if not low_stock_items.empty:
        st.warning("⚠️ Low Stock Alert!")
        with st.expander("View Low Stock Items", expanded=True):
            for _, item in low_stock_items.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['name']}**")
                with col2:
                    st.write(f"Stock: {item['quantity']}")
                with col3:
                    st.write(f"Min: {item['min_quantity']}")
    
    st.subheader("Products Table")
    
    # Search functionality
    search_term = st.text_input(
        "🔍 Search products", 
        placeholder="Type to search by product name...",
        help="Search is case-insensitive"
    )
    
    # Get products based on search
    if search_term:
        products_df = search_products(search_term)
        if products_df.empty:
            st.info(f"No products found matching '{search_term}'")
            return
    else:
        products_df = get_all_products()
        if products_df.empty:
            st.info("No products found. Add some products to get started!")
            if st.button("➕ Add Your First Product"):
                st.info("👆 Use the sidebar to navigate to 'Add Product' page")
            return
    
    # Display products table
    display_df = prepare_display_dataframe(products_df)
    
    # Show products count
    st.write(f"Showing {len(display_df)} product(s)")
    
    # Display the dataframe
    st.dataframe(
        display_df, 
        use_container_width=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Product Name": st.column_config.TextColumn("Product Name", width="large"),
            "Quantity": st.column_config.NumberColumn("Quantity", width="small"),
            "Min Qty": st.column_config.NumberColumn("Min Qty", width="small"),
            "Price": st.column_config.TextColumn("Price", width="medium"),
            "Cost": st.column_config.TextColumn("Cost", width="medium"),
            "Created Date": st.column_config.DatetimeColumn("Created Date", width="medium")
        }
    )
    
    # Delete product section
    show_delete_section(products_df)

def prepare_display_dataframe(products_df):
    """Prepare dataframe for display"""
    display_df = products_df.copy()
    display_df['Price'] = display_df['price'].apply(format_currency)
    display_df['Cost'] = display_df['cost'].apply(format_currency)
    
    # Select and rename columns for display
    display_df = display_df[[
        'product_id', 'name', 'quantity', 'min_quantity', 
        'Price', 'Cost', 'created_date'
    ]]
    display_df.columns = [
        'ID', 'Product Name', 'Quantity', 'Min Qty', 
        'Price', 'Cost', 'Created Date'
    ]
    
    return display_df

def show_delete_section(products_df):
    """Show the delete product section"""
    if products_df.empty:
        return
    
    st.subheader("🗑️ Delete Product")
    
    with st.expander("Delete a Product", expanded=False):
        # Product selection
        product_options = {
            row['product_id']: f"{row['name']} (ID: {row['product_id']})"
            for _, row in products_df.iterrows()
        }
        
        selected_product_id = st.selectbox(
            "Select product to delete",
            options=list(product_options.keys()),
            format_func=lambda x: product_options[x],
            help="This action cannot be undone"
        )
        
        if selected_product_id:
            selected_product = products_df[
                products_df['product_id'] == selected_product_id
            ].iloc[0]
            
            # Show product details
            st.info(f"""
            **Product Details:**
            - Name: {selected_product['name']}
            - Current Stock: {selected_product['quantity']}
            - Price: {format_currency(selected_product['price'])}
            """)
            
            # Confirmation
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("🗑️ Delete Product", type="secondary"):
                    try:
                        success = delete_product(selected_product_id)
                        if success:
                            st.success(f"✅ Product '{selected_product['name']}' deleted successfully!")
                            st.info("🔄 Please refresh the page to see updated results.")
                        else:
                            st.error("❌ Product not found or could not be deleted")
                    except Exception as e:
                        st.error(f"❌ Error deleting product: {str(e)}")
            
            with col2:
                st.warning("⚠️ **Warning:** This will permanently delete the product and all related transaction history.")

if __name__ == "__main__":
    show_view_products_page()