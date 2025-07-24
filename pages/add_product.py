# pages/add_product.py
import streamlit as st
from database.operations import add_product
from utils.validation import validate_product_data

def show_add_product_page():
    """Yeni məhsul əlavə etmə səhifəsini göstər"""
    st.header("Yeni Məhsul Əlavə Et")
    
    # Add refresh button for cache
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Yenilə"):
            st.cache_data.clear()
            st.rerun()
    
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Məhsul Adı*", 
                placeholder="Məhsul adını daxil edin",
                help="Tələb olunan sahə"
            )
            quantity = st.number_input(
                "Hazırki Miqdar*", 
                min_value=0, 
                value=0, 
                step=1,
                help="Hazırki stok miqdarı"
            )
            min_quantity = st.number_input(
                "Minimum Miqdar (Yenidən Sifariş Səviyyəsi)", 
                min_value=0, 
                value=5, 
                step=1,
                help="Stok bu səviyyəyə düşdükdə xəbərdarlıq göstər"
            )
        
        with col2:
            price = st.number_input(
                "Satış Qiyməti*", 
                min_value=0.0, 
                value=0.0, 
                step=0.01, 
                format="%.2f",
                help="Tələb olunan sahə"
            )
            cost = st.number_input(
                "Alış Qiyməti", 
                min_value=0.0, 
                value=0.0, 
                step=0.01, 
                format="%.2f",
                help="İstəyə bağlı: Mənfəət hesablaması üçün alış qiyməti"
            )
        
        # Show profit calculation preview if both price and cost are entered
        if price > 0 and cost > 0:
            profit = price - cost
            profit_margin = (profit / price) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                if profit > 0:
                    st.success(f"💰 Mənfəət: ₼{profit:.2f}")
                else:
                    st.error(f"📉 Zərər: ₼{abs(profit):.2f}")
            with col2:
                if profit > 0:
                    st.info(f"📊 Mənfəət payı: {profit_margin:.1f}%")
        
        # Form submission
        submitted = st.form_submit_button("Məhsul Əlavə Et", type="primary")
        
        if submitted:
            # Validate input
            errors = validate_product_data(name, price, quantity, min_quantity, cost)
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    with st.spinner("Məhsul əlavə edilir..."):
                        product_id = add_product(
                            name.strip(), 
                            quantity, 
                            min_quantity, 
                            price, 
                            cost
                        )
                    
                    st.success(f"✅ '{name.strip()}' məhsulu uğurla əlavə edildi! (ID: {product_id})")
                    st.balloons()  # Celebration effect
                    
                    # Show success info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.info("🔄 Form təmizləndi. Başqa məhsul əlavə edə bilərsiniz.")
                    with col2:
                        if st.button("📦 Bütün Məhsulları Gör"):
                            st.switch_page("pages/view_products.py")
                    
                    # Cache is automatically cleared by the add_product function
                    
                except Exception as e:
                    st.error(f"❌ Məhsul əlavə edərkən xəta: {str(e)}")
    
    # Help section
    with st.expander("ℹ️ Kömək - Məhsul Əlavə Etmək"):
        st.markdown("""
        **Tələb Olunan Sahələr (*):
        - **Məhsul Adı**: Ən azı 2 simvol olmalıdır
        - **Satış Qiyməti**: 0-dan böyük olmalıdır
        
        **İstəyə Bağlı Sahələr:**
        - **Hazırki Miqdar**: Başlanğıc stok (standart: 0)
        - **Minimum Miqdar**: Yenidən sifariş xəbərdarlıq səviyyəsi (standart: 5)
        - **Alış Qiyməti**: Mənfəət izləmə üçün (standart: 0)
        
        **Məsləhətlər:**
        - 💡 Alış qiyməti daxil etsəniz, mənfəət hesablanacaq
        - 📊 Minimum miqdar az stok xəbərdarlıqları üçün istifadə olunur
        - 🔄 Məhsul əlavə etdikdən sonra cache avtomatik təmizlənir
        """)

if __name__ == "__main__":
    show_add_product_page()