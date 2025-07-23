# pages/add_product.py
import streamlit as st
from database.operations import add_product
from utils.validation import validate_product_data

def show_add_product_page():
    """Display the add product page"""
    st.header("Add New Product")
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Product Name*", 
                placeholder="Enter product name",
                help="Required field"
            )
            quantity = st.number_input(
                "Current Quantity*", 
                min_value=0, 
                value=0, 
                step=1,
                help="Current stock quantity"
            )
            min_quantity = st.number_input(
                "Minimum Quantity (Reorder Level)", 
                min_value=0, 
                value=5, 
                step=1,
                help="Alert when stock drops to this level"
            )
        
        with col2:
            price = st.number_input(
                "Selling Price*", 
                min_value=0.0, 
                value=0.0, 
                step=0.01, 
                format="%.2f",
                help="Required field"
            )
            cost = st.number_input(
                "Purchase Cost", 
                min_value=0.0, 
                value=0.0, 
                step=0.01, 
                format="%.2f",
                help="Optional: Cost price for profit calculation"
            )
        
        # Form submission
        submitted = st.form_submit_button("Add Product", type="primary")
        
        if submitted:
            # Validate input
            errors = validate_product_data(name, price, quantity, min_quantity, cost)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    product_id = add_product(
                        name.strip(), 
                        quantity, 
                        min_quantity, 
                        price, 
                        cost
                    )
                    st.success(f"✅ Product '{name.strip()}' added successfully! (ID: {product_id})")
                    st.info("🔄 Form has been reset. You can add another product or go to 'View Products' to see all items.")
                except Exception as e:
                    st.error(f"❌ Error adding product: {str(e)}")
    
    # Help section
    with st.expander("ℹ️ Help - Adding Products"):
        st.markdown("""
        **Required Fields (marked with *):**
        - **Product Name**: Must be at least 2 characters long
        - **Selling Price**: Must be greater than 0
        
        **Optional Fields:**
        - **Current Quantity**: Starting stock (default: 0)
        - **Minimum Quantity**: Reorder alert level (default: 5)
        - **Purchase Cost**: For profit tracking (default: 0)
        """)

if __name__ == "__main__":
    show_add_product_page()