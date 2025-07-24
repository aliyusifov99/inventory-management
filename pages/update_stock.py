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
    """Stok yenilənməsi səhifəsini göstər"""
    st.header("📈 Stoku Yenilə")
    
    # Bütün məhsulları əldə et
    products_df = get_all_products()
    
    if products_df.empty:
        st.info("Heç bir məhsul tapılmadı. Stoku yeniləmək üçün əvvəlcə bəzi məhsullar əlavə edin.")
        return
    
    # Müxtəlif əməliyyatlar üçün tablar yaradın
    tab1, tab2, tab3 = st.tabs(["📦 Stok Daxil/Xaric", "✏️ Məhsulu Redaktə Et", "📋 Əməliyyat Tarixçəsi"])
    
    with tab1:
        show_stock_update_tab(products_df)
    
    with tab2:
        show_edit_product_tab(products_df)
    
    with tab3:
        show_transaction_history_tab(products_df)

def show_stock_update_tab(products_df):
    """Stok miqdarlarını yeniləmək üçün tab"""
    st.subheader("Stok Miqdarını Yenilə")
    
    # Məhsul seçimi
    product_options = {
        row['product_id']: f"{row['name']} (Hazırki: {int(row['quantity'])}) - {format_currency(float(row['price']))}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Məhsul Seçin",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        help="Stokunu yeniləmək üçün məhsul seçin"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        # Hazırki məhsul məlumatını göstər
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hazırki Stok", int(selected_product['quantity']))
        with col2:
            st.metric("Minimum Səviyyə", int(selected_product['min_quantity']))
        with col3:
            st.metric("Qiymət", format_currency(float(selected_product['price'])))
        
        # Stok yenilənməsi forması
        with st.form("update_stock_form"):
            st.subheader("Stok Hərəkəti")
            
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox(
                    "Əməliyyat Növü",
                    ["SATIŞ", "STOKU ARTIR"],
                    help="SALE: Stoku azaldır, RESTOCK: Stoku artırır"
                )
            
            with col2:
                quantity_change = st.number_input(
                    "Miqdar",
                    min_value=1,
                    value=1,
                    step=1,
                    help="Stokdan əlavə ediləcək və ya çıxarılacaq miqdar"
                )
            
            # Dəyişikliyin önizləməsini göstər
            current_stock = int(selected_product['quantity'])
            if transaction_type == "SALE":
                new_stock = current_stock - quantity_change
                change_text = f"Stok azalacaq: {current_stock} → {new_stock}"
                if new_stock < 0:
                    st.error(f"⚠️ Kifayət qədər stok yoxdur! Hazırki: {current_stock}, Satmağa çalışılan: {quantity_change}")
            else:  # RESTOCK
                new_stock = current_stock + quantity_change
                change_text = f"Stok artacaq: {current_stock} → {new_stock}"
            
            st.info(change_text)
            
            # Az stok xəbərdarlığı
            if new_stock <= int(selected_product['min_quantity']):
                st.warning(f"⚠️ Stok minimum səviyyədə və ya altında olacaq ({int(selected_product['min_quantity'])})")
            
            submitted = st.form_submit_button("Stoku Yenilə", type="primary")
            
            if submitted:
                if transaction_type == "SALE" and quantity_change > current_stock:
                    st.error("❌ Stokda olandan çox məhsul satmaq olmaz!")
                else:
                    try:
                        # Yeni miqdarı hesabla
                        if transaction_type == "SALE":
                            new_quantity = current_stock - quantity_change
                            quantity_change_db = -quantity_change  # Satışlar üçün mənfi
                        else:  # RESTOCK
                            new_quantity = current_stock + quantity_change
                            quantity_change_db = quantity_change  # Stok əlavəsi üçün müsbət
                        
                        # Stoku yenilə və əməliyyat əlavə et
                        update_product_stock(selected_product_id, new_quantity)
                        add_transaction(selected_product_id, transaction_type, quantity_change_db)
                        
                        st.success(f"✅ Stok uğurla yeniləndi!")
                        st.success(f"📊 {selected_product['name']}: {current_stock} → {new_quantity}")
                        
                        # Yenilənmiş məlumatı avtomatik göstər
                        st.info("🔄 Yenilənmiş stok səviyyələrini görmək üçün səhifəni yeniləyin.")
                        
                    except Exception as e:
                        st.error(f"❌ Stok yeniləməkdə xəta: {str(e)}")

def show_edit_product_tab(products_df):
    """Məhsul təfərrüatlarını redaktə etmək üçün tab"""
    st.subheader("Məhsul Təfərrüatlarını Redaktə Et")
    
    # Məhsul seçimi
    product_options = {
        row['product_id']: f"{row['name']} - {format_currency(row['price'])}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Redaktə Ediləcək Məhsulu Seçin",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        key="edit_product_select"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        # Redaktə forması
        with st.form("edit_product_form"):
            st.subheader(f"Redaktə: {selected_product['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Məhsul Adı", 
                    value=selected_product['name'],
                    help="Məhsul adını yenilə"
                )
                new_min_quantity = st.number_input(
                    "Minimum Miqdar", 
                    min_value=0, 
                    value=int(selected_product['min_quantity']),
                    step=1,
                    help="Yenidən sifariş səviyyəsini yenilə"
                )
            
            with col2:
                new_price = st.number_input(
                    "Satış Qiyməti", 
                    min_value=0.0, 
                    value=float(selected_product['price']),
                    step=0.01,
                    format="%.2f",
                    help="Satış qiymətini yenilə"
                )
                new_cost = st.number_input(
                    "Alış Qiyməti", 
                    min_value=0.0, 
                    value=float(selected_product['cost']),
                    step=0.01,
                    format="%.2f",
                    help="Alış qiymətini yenilə"
                )
            
            st.info("ℹ️ Qeyd: Bu, hazırki stok miqdarını dəyişməyəcək. Miqdarları yeniləmək üçün 'Stok Daxil/Xaric' tabından istifadə edin.")
            
            submitted = st.form_submit_button("Məhsulu Yenilə", type="primary")
            
            if submitted:
                if not new_name or new_name.strip() == "":
                    st.error("❌ Məhsul adı boş ola bilməz!")
                elif new_price <= 0:
                    st.error("❌ Qiymət 0-dan böyük olmalıdır!")
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
                        st.success(f"✅ Məhsul '{new_name.strip()}' uğurla yeniləndi!")
                        st.info("🔄 Yenilənmiş təfərrüatları görmək üçün səhifəni yeniləyin.")
                        
                    except Exception as e:
                        st.error(f"❌ Məhsul yeniləməkdə xəta: {str(e)}")

def show_transaction_history_tab(products_df):
    """Əməliyyat tarixçəsini görmək üçün tab"""
    st.subheader("Əməliyyat Tarixçəsi")
    
    # Məhsul seçimi
    product_options = {
        row['product_id']: f"{row['name']}"
        for _, row in products_df.iterrows()
    }
    
    selected_product_id = st.selectbox(
        "Tarixçəsini Görəcəyiniz Məhsulu Seçin",
        options=list(product_options.keys()),
        format_func=lambda x: product_options[x],
        key="history_product_select"
    )
    
    if selected_product_id:
        selected_product = products_df[products_df['product_id'] == selected_product_id].iloc[0]
        
        st.subheader(f"Tarixçə: {selected_product['name']}")
        
        # Əməliyyatları əldə et
        transactions_df = get_product_transactions(selected_product_id)
        
        if transactions_df.empty:
            st.info("Bu məhsul üçün heç bir əməliyyat tapılmadı.")
        else:
            # Xülasəni göstər
            col1, col2, col3 = st.columns(3)
            
            sales_count = len(transactions_df[transactions_df['transaction_type'] == 'SALE'])
            restock_count = len(transactions_df[transactions_df['transaction_type'] == 'RESTOCK'])
            total_sold = abs(transactions_df[transactions_df['transaction_type'] == 'SALE']['quantity_change'].sum())
            
            with col1:
                st.metric("Ümumi Satışlar", sales_count)
            with col2:
                st.metric("Ümumi Stok Əlavələri", restock_count)
            with col3:
                st.metric("Satılan Məhsullar", int(total_sold))
            
            # Əməliyyat cədvəlini göstər
            st.subheader("Son Əməliyyatlar")
            
            # Göstərmək üçün məlumat çərçivəsini formatla
            display_df = transactions_df.copy()
            display_df['Tarix'] = display_df['timestamp']
            display_df['Növ'] = display_df['transaction_type']
            display_df['Dəyişiklik'] = display_df['quantity_change'].apply(
                lambda x: f"+{x}" if x > 0 else str(x)
            )
            
            # Göstərmək üçün sütunları seç
            display_df = display_df[['Tarix', 'Növ', 'Dəyişiklik']].sort_values('Tarix', ascending=False)
            
            st.dataframe(
                display_df, 
                use_container_width=True,
                column_config={
                    "Tarix": st.column_config.DatetimeColumn("Tarix və Vaxt", width="large"),
                    "Növ": st.column_config.TextColumn("Növ", width="medium"),
                    "Dəyişiklik": st.column_config.TextColumn("Miqdar Dəyişikliyi", width="small")
                }
            )

if __name__ == "__main__":
    show_update_stock_page()