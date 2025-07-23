# app.py
import streamlit as st
from config.settings import APP_TITLE, APP_ICON, PAGE_LAYOUT, IS_CLOUD_DEPLOYMENT, DB_TYPE, GOOGLE_SHEETS_URL
from config.database import init_database, test_connection
from pages.add_product import show_add_product_page
from pages.view_products import show_view_products_page
from pages.update_stock import show_update_stock_page
from pages.dashboard import show_dashboard_page

def main():
    """Main application function"""
    # Configure Streamlit page
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Initialize database
    init_database()
    
    # App header
    st.title(f"{APP_ICON} {APP_TITLE}")
    
    # Show deployment and database status
    status_container = st.container()
    with status_container:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if IS_CLOUD_DEPLOYMENT:
                if DB_TYPE == "sheets":
                    st.success("☁️ **Streamlit Cloud** + 📊 **Google Sheets**")
                else:
                    st.success("☁️ **Streamlit Cloud** + 🗄️ **SQLite**")
            else:
                if DB_TYPE == "sheets":
                    st.info("💻 **Local Development** + 📊 **Google Sheets**")
                else:
                    st.info("💻 **Local Development** + 🗄️ **SQLite**")
        
        with col2:
            st.caption(f"Database: {DB_TYPE.upper()}")
        
        with col3:
            # Test connection
            if test_connection():
                st.success("🟢 Connected")
            else:
                st.error("🔴 Failed")
                if not IS_CLOUD_DEPLOYMENT:
                    st.stop()
    
    # Show Google Sheets link if using sheets
    if DB_TYPE == "sheets" and GOOGLE_SHEETS_URL:
        st.info(f"📊 **Database**: [View Google Sheet]({GOOGLE_SHEETS_URL})")
    
    st.markdown("---")  # Separator
    
    # Sidebar navigation
    st.sidebar.title("📋 Navigation")
    
    # Navigation menu
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "View Products", "Add Product", "Update Stock"],
        help="Select a page to navigate"
    )
    
    # Add some spacing
    st.sidebar.markdown("---")
    
    # Show app info in sidebar
    with st.sidebar.expander("ℹ️ About"):
        st.markdown("""
        **Inventory Management System v1.0**
        
        **Phase 4 Features:**
        - ✅ Add new products
        - ✅ View all products
        - ✅ Search products
        - ✅ Low stock alerts
        - ✅ Delete products
        - ✅ Basic statistics
        - ✅ Update stock (sales/restock)
        - ✅ Edit product details
        - ✅ Transaction history
        - ✅ Advanced dashboard
        - ✅ Sales analytics
        - ✅ Inventory analysis
        - ✅ Reports & exports
        - ✅ Cloud deployment
        - ✅ Multi-device access
        - ✅ Public URL access
        
        **Coming Soon:**
        - 📊 Advanced dashboard
        - 📈 Stock movements
        - 📱 Transaction history
        - ☁️ Cloud database
        """)
    
    # Route to appropriate page
    if page == "Dashboard":
        show_dashboard_page()
    elif page == "Add Product":
        show_add_product_page()
    elif page == "View Products":
        show_view_products_page()
    elif page == "Update Stock":
        show_update_stock_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Built with ❤️ using Streamlit*")

if __name__ == "__main__":
    main()