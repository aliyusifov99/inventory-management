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
    """Məhsulları görüntüləmə səhifəsini göstər"""
    st.header("Bütün Məhsullar")
    
    # Add refresh button for cache
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Yenilə"):
            st.cache_data.clear()
            st.rerun()
    
    # Get cached inventory statistics
    with st.spinner("Statistikalar yüklənir..."):
        stats = get_inventory_stats()
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Ümumi Məhsullar", stats['total_products'])
    
    with col2:
        st.metric("Stok Dəyəri", format_currency(stats['total_value']))
    
    with col3:
        st.metric("Az Stoklu Məhsullar", stats['low_stock_count'])
    
    with col4:
        st.metric("Ümumi Ədəd", stats['total_items'])
    
    # Low stock alerts (cached)
    with st.spinner("Az stok məlumatları yoxlanır..."):
        low_stock_items = get_low_stock_products()
    
    if not low_stock_items.empty:
        st.warning("⚠️ Az Stok Xəbərdarlığı!")
        with st.expander("Az Stoklu Məhsulları Gör", expanded=True):
            for _, item in low_stock_items.iterrows():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{item['name']}**")
                with col2:
                    st.write(f"Stok: {item['quantity']}")
                with col3:
                    st.write(f"Min: {item['min_quantity']}")
    
    st.subheader("Məhsullar Cədvəli")
    
    # Search functionality
    search_term = st.text_input(
        "🔍 Məhsul axtarın", 
        placeholder="Məhsul adı ilə axtarmaq üçün yazın...",
        help="Axtarış böyük-kiçik hərfə həssas deyil"
    )
    
    # Get products based on search (cached)
    with st.spinner("Məhsullar yüklənir..."):
        if search_term:
            products_df = search_products(search_term)
            if products_df.empty:
                st.info(f"'{search_term}' sorğusuna uyğun məhsul tapılmadı")
                return
        else:
            products_df = get_all_products()
            if products_df.empty:
                st.info("Heç bir məhsul tapılmadı. Başlamaq üçün bəzi məhsullar əlavə edin!")
                if st.button("➕ İlk Məhsulunuzu Əlavə Edin"):
                    st.info("👆 'Məhsul Əlavə Et' səhifəsinə getmək üçün yan paneldən istifadə edin")
                return
    
    # Display products table
    display_df = prepare_display_dataframe(products_df)
    
    # Show products count
    st.write(f"{len(display_df)} məhsul göstərilir")
    
    # Display the dataframe
    st.dataframe(
        display_df, 
        use_container_width=True,
        column_config={
            "ID": st.column_config.NumberColumn("ID", width="small"),
            "Məhsul Adı": st.column_config.TextColumn("Məhsul Adı", width="large"),
            "Miqdar": st.column_config.NumberColumn("Miqdar", width="small"),
            "Min Miqdar": st.column_config.NumberColumn("Min Miqdar", width="small"),
            "Qiymət": st.column_config.TextColumn("Qiymət", width="medium"),
            "Maya": st.column_config.TextColumn("Maya", width="medium"),
            "Yaradılma Tarixi": st.column_config.DatetimeColumn("Yaradılma Tarixi", width="medium")
        }
    )
    
    # Delete product section
    show_delete_section(products_df)

@st.cache_data(ttl=60)  # Cache display dataframe preparation
def prepare_display_dataframe(products_df):
    """Göstərmək üçün məlumat çərçivəsini hazırla (cached)"""
    display_df = products_df.copy()
    display_df['Qiymət'] = display_df['price'].apply(format_currency)
    display_df['Maya'] = display_df['cost'].apply(format_currency)
    
    # Select and rename columns for display
    display_df = display_df[[
        'product_id', 'name', 'quantity', 'min_quantity', 
        'Qiymət', 'Maya', 'created_date'
    ]]
    display_df.columns = [
        'ID', 'Məhsul Adı', 'Miqdar', 'Min Miqdar', 
        'Qiymət', 'Maya', 'Yaradılma Tarixi'
    ]
    
    return display_df

def show_delete_section(products_df):
    """Məhsul silmə bölməsini göstər"""
    if products_df.empty:
        return
    
    st.subheader("🗑️ Məhsul Sil")
    
    with st.expander("Məhsul Sil", expanded=False):
        # Product selection
        product_options = {
            row['product_id']: f"{row['name']} (ID: {row['product_id']})"
            for _, row in products_df.iterrows()
        }
        
        selected_product_id = st.selectbox(
            "Silinəcək məhsulu seçin",
            options=list(product_options.keys()),
            format_func=lambda x: product_options[x],
            help="Bu əməliyyat geri qaytarıla bilməz"
        )
        
        if selected_product_id:
            selected_product = products_df[
                products_df['product_id'] == selected_product_id
            ].iloc[0]
            
            # Show product details
            st.info(f"""
            **Məhsul Məlumatları:**
            - Ad: {selected_product['name']}
            - Hazırki Stok: {selected_product['quantity']}
            - Qiymət: {format_currency(selected_product['price'])}
            """)
            
            # Confirmation
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("🗑️ Məhsulu Sil", type="secondary"):
                    try:
                        with st.spinner("Məhsul silinir..."):
                            success = delete_product(selected_product_id)
                        if success:
                            st.success(f"✅ '{selected_product['name']}' məhsulu uğurla silindi!")
                            st.info("🔄 Yenilənmiş nəticələri görmək üçün səhifəni yeniləyin.")
                            # Clear cache after deletion
                            st.cache_data.clear()
                        else:
                            st.error("❌ Məhsul tapılmadı və ya silinə bilmədi")
                    except Exception as e:
                        st.error(f"❌ Məhsul silərkən xəta: {str(e)}")
            
            with col2:
                st.warning("⚠️ **Xəbərdarlıq:** Bu, məhsulu və bütün əlaqəli əməliyyat tarixçəsini həmişəlik siləcək.")

if __name__ == "__main__":
    show_view_products_page()