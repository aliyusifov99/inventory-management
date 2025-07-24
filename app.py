# app.py
import streamlit as st
from config.settings import APP_TITLE, APP_ICON, PAGE_LAYOUT, IS_CLOUD_DEPLOYMENT, DB_TYPE
from config.database import init_database, test_connection
from pages.add_product import show_add_product_page
from pages.view_products import show_view_products_page
from pages.update_stock import show_update_stock_page
from pages.dashboard import show_dashboard_page

def main():
    """Əsas tətbiq funksiyası"""
    # Streamlit səhifəsini konfiqurasiya et
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state="expanded"
    )
    
    # Məlumat bazasını başlat
    try:
        init_database()
        # Cədvəllərin mövcudluğunu yoxla
        if not test_connection():
            st.error("❌ Məlumat bazası bağlantısı uğursuz")
            st.stop()
    except Exception as e:
        st.error(f"❌ Məlumat bazası başlatma uğursuz: {str(e)}")
        
        # Supabase üçün bağlantı köməyi göstər
        if IS_CLOUD_DEPLOYMENT and DB_TYPE == "postgres":
            st.warning("🔧 **Supabase Bağlantı Problemi**")
            st.info("""
            **Tez Həll**: Streamlit Cloud tətbiq ayarları → Secrets bölməsinə əlavə edin:
            ```
            DB_TYPE = "postgres"
            SUPABASE_HOST = "db.your-project.supabase.co"
            SUPABASE_PORT = "5432"
            SUPABASE_DATABASE = "postgres"
            SUPABASE_USER = "postgres"
            SUPABASE_PASSWORD = "your-password"
            ```
            
            **Və ya müvəqqəti SQLite istifadə edin**:
            ```
            DB_TYPE = "sqlite"
            ```
            """)
        elif DB_TYPE == "postgres":
            st.warning("🔧 **Supabase Bağlantı Problemi**")
            st.info(f"""
            **Xəta Təfərrüatları**: {str(e)}
            
            **.env faylınızı yoxlayın**:
            - SUPABASE_HOST-un düzgün olduğuna əmin olun
            - SUPABASE_PASSWORD-un Supabase layihənizlə uyğun olduğunu təsdiqləyin
            - Supabase layihənizin işlədiyinə əmin olun
            
            **Və ya müvəqqəti SQLite-a keçin**:
            .env faylınızda `DB_TYPE=sqlite` dəyişin
            """)
        st.stop()
    
    # Tətbiq başlığı
    st.title(f"{APP_ICON} {APP_TITLE}")
    
    # Yerləşdirmə və məlumat bazası vəziyyətini göstər
    status_container = st.container()
    with status_container:
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            st.caption(f"Məlumat bazası: {DB_TYPE.upper()}")
        
        with col3:
            # Bağlantını test et
            if test_connection():
                st.success("🟢 Bağlanıb")
            else:
                st.error("🔴 Uğursuz")
                if not IS_CLOUD_DEPLOYMENT:
                    st.stop()
    
    st.markdown("---")  # Ayırıcı
    
    # TƏMİZ YAN PANEL - YALNIZ NAVİQASİYA
    st.sidebar.title("📋 Menyu")
    
    # Naviqasiya menyusu
    page = st.sidebar.radio(
        "Səhifə seçin",
        ["Ana Səhifə", "Məhsulları Gör", "Məhsul Əlavə Et", "Stoku Yenilə"],
        label_visibility="collapsed"
    )
    
    # Sadə altbilgi
    st.sidebar.markdown("---")
    st.sidebar.markdown("*Anbar İdarəetmə Sistemi*")
    
    # Müvafiq səhifəyə yönləndirin
    if page == "Ana Səhifə":
        show_dashboard_page()
    elif page == "Məhsul Əlavə Et":
        show_add_product_page()
    elif page == "Məhsulları Gör":
        show_view_products_page()
    elif page == "Stoku Yenilə":
        show_update_stock_page()

if __name__ == "__main__":
    main()