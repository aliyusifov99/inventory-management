# pages/add_product.py
import streamlit as st
from database.operations import add_product
from utils.validation import validate_product_data

def show_add_product_page():
    """Yeni məhsul əlavə etmə səhifəsini göstər"""
    st.header("Yeni Məhsul Əlavə Et")
    
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
        
        # Forma təqdimi
        submitted = st.form_submit_button("Məhsul Əlavə Et", type="primary")
        
        if submitted:
            # Girişi yoxla
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
                    st.success(f"✅ '{name.strip()}' məhsulu uğurla əlavə edildi! (ID: {product_id})")
                    st.info("🔄 Form sıfırlandı. Başqa məhsul əlavə edə bilərsiniz və ya bütün məhsulları görmək üçün 'Məhsulları Gör' səhifəsinə gedin.")
                except Exception as e:
                    st.error(f"❌ Məhsul əlavə edərkən xəta: {str(e)}")
    
    # Kömək bölməsi
    with st.expander("ℹ️ Kömək - Məhsul Əlavə Etmək"):
        st.markdown("""
        **Tələb Olunan Sahələr (*):
        - **Məhsul Adı**: Ən azı 2 simvol olmalıdır
        - **Satış Qiyməti**: 0-dan böyük olmalıdır
        
        **İstəyə Bağlı Sahələr:**
        - **Hazırki Miqdar**: Başlanğıc stok (standart: 0)
        - **Minimum Miqdar**: Yenidən sifariş xəbərdarlıq səviyyəsi (standart: 5)
        - **Alış Qiyməti**: Mənfəət izləmə üçün (standart: 0)
        """)

if __name__ == "__main__":
    show_add_product_page()