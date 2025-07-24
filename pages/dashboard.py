# pages/dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.operations import (
    get_all_products,
    get_all_transactions,
    get_inventory_stats
)
from utils.validation import format_currency

# Cache chart generation functions
@st.cache_data(ttl=120)  # Cache charts for 2 minutes
def generate_stock_chart(products_df):
    """Generate stock levels chart (cached)"""
    if products_df.empty:
        return None
    
    fig_stock = px.bar(
        products_df.head(10), 
        x='name', 
        y='quantity',
        title='📦 Hazırki Stok Səviyyələri (İlk 10)',
        color='quantity',
        color_continuous_scale='RdYlGn'
    )
    fig_stock.update_xaxes(title="Məhsul", tickangle=45)
    fig_stock.update_yaxes(title="Miqdar")
    fig_stock.update_layout(height=400)
    return fig_stock

@st.cache_data(ttl=120)  # Cache charts for 2 minutes
def generate_activity_chart(transactions_df):
    """Generate recent activity chart (cached)"""
    if transactions_df.empty:
        return None
    
    # Process recent transactions
    recent_transactions = transactions_df.head(7)
    recent_transactions['date'] = pd.to_datetime(recent_transactions['timestamp']).dt.date
    daily_activity = recent_transactions.groupby(['date', 'transaction_type']).size().reset_index(name='count')
    
    fig_activity = px.bar(
        daily_activity,
        x='date',
        y='count',
        color='transaction_type',
        title='📅 Son Fəaliyyət (Son 7 gün)',
        color_discrete_map={'SALE': '#ff6b6b', 'RESTOCK': '#51cf66'}
    )
    fig_activity.update_xaxes(title="Tarix")
    fig_activity.update_yaxes(title="Əməliyyat Sayı")
    fig_activity.update_layout(height=400)
    return fig_activity

@st.cache_data(ttl=180)  # Cache for 3 minutes
def generate_sales_charts(sales_df, products_df):
    """Generate sales analytics charts (cached)"""
    charts = {}
    
    if not sales_df.empty:
        # Top selling products
        product_sales = sales_df.groupby('product_name')['quantity_change'].apply(lambda x: abs(x).sum()).reset_index()
        product_sales = product_sales.sort_values('quantity_change', ascending=False).head(10)
        
        if not product_sales.empty:
            charts['top_selling'] = px.bar(
                product_sales,
                x='quantity_change',
                y='product_name',
                orientation='h',
                title='🏆 Ən Çox Satılan Məhsullar',
                color='quantity_change',
                color_continuous_scale='Blues'
            )
            charts['top_selling'].update_xaxes(title="Satılan Vahid")
            charts['top_selling'].update_yaxes(title="Məhsul")
            charts['top_selling'].update_layout(height=400)
        
        # Sales trend
        sales_df['date'] = pd.to_datetime(sales_df['timestamp']).dt.date
        daily_sales = sales_df.groupby('date')['quantity_change'].apply(lambda x: abs(x).sum()).reset_index()
        
        if len(daily_sales) > 1:
            charts['trend'] = px.line(
                daily_sales,
                x='date',
                y='quantity_change',
                title='📈 Satış Tendensiyası',
                markers=True
            )
            charts['trend'].update_xaxes(title="Tarix")
            charts['trend'].update_yaxes(title="Satılan Məhsullar")
            charts['trend'].update_layout(height=400)
    
    return charts

@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_inventory_charts(products_df):
    """Generate inventory analysis charts (cached)"""
    charts = {}
    
    if not products_df.empty:
        # Stock distribution
        stock_ranges = []
        
        for _, product in products_df.iterrows():
            qty = product['quantity']
            min_qty = product['min_quantity']
            
            if qty == 0:
                stock_ranges.append('Stokda Yoxdur')
            elif qty <= min_qty:
                stock_ranges.append('Az Stok')
            elif qty <= min_qty * 2:
                stock_ranges.append('Normal Stok')
            else:
                stock_ranges.append('Yüksək Stok')
        
        stock_dist = pd.Series(stock_ranges).value_counts()
        
        charts['distribution'] = px.pie(
            values=stock_dist.values,
            names=stock_dist.index,
            title='📊 Stok Səviyyəsi Paylanması',
            color_discrete_map={
                'Stokda Yoxdur': '#ff6b6b',
                'Az Stok': '#feca57',
                'Normal Stok': '#48dbfb',
                'Yüksək Stok': '#1dd1a1'
            }
        )
        charts['distribution'].update_layout(height=400)
        
        # Value analysis
        products_df_copy = products_df.copy()
        products_df_copy['total_value'] = products_df_copy['quantity'] * products_df_copy['price']
        top_value = products_df_copy.nlargest(10, 'total_value')
        
        charts['value'] = px.bar(
            top_value,
            x='total_value',
            y='name',
            orientation='h',
            title='💎 Ən Yüksək Dəyərli Anbar',
            color='total_value',
            color_continuous_scale='Greens'
        )
        charts['value'].update_xaxes(title="Ümumi Dəyər (₼)")
        charts['value'].update_yaxes(title="Məhsul")
        charts['value'].update_layout(height=400)
    
    return charts

def show_dashboard_page():
    """Ana səhifə və analitika bölməsini göstər"""
    st.header("📊 Ana Səhifə və Analitika")
    
    # Add a refresh button to clear cache manually
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🔄 Yenilə"):
            st.cache_data.clear()
            st.rerun()
    
    # Get cached data
    with st.spinner("Məlumatlar yüklənir..."):
        products_df = get_all_products()
        transactions_df = get_all_transactions()
        stats = get_inventory_stats()
    
    if products_df.empty:
        st.info("Məlumat mövcud deyil. Analitika görmək üçün bəzi məhsullar əlavə edin.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Ümumi Baxış", "💰 Satış Analitikası", "📦 Anbar Analizi", "📋 Hesabatlar"])
    
    with tab1:
        show_overview_tab(products_df, transactions_df, stats)
    
    with tab2:
        show_sales_analytics_tab(products_df, transactions_df)
    
    with tab3:
        show_inventory_analysis_tab(products_df)
    
    with tab4:
        show_reports_tab(products_df, transactions_df)

def show_overview_tab(products_df, transactions_df, stats):
    """Əsas göstəricilər ilə ümumi baxış paneli"""
    st.subheader("📈 Biznes Ümumi Baxışı")
    
    # Əsas Göstəricilər Sırası
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Ümumi Məhsullar", 
            stats['total_products'],
            help="Unikal məhsulların ümumi sayı"
        )
    
    with col2:
        st.metric(
            "Stok Dəyəri", 
            format_currency(stats['total_value']),
            help="Hazırki anbarın ümumi dəyəri"
        )
    
    with col3:
        st.metric(
            "Az Stoklu Məhsullar", 
            stats['low_stock_count'],
            delta=f"-{stats['low_stock_count']}" if stats['low_stock_count'] > 0 else "0",
            delta_color="inverse",
            help="Minimum səviyyədə və ya altında olan məhsullar"
        )
    
    with col4:
        total_sales = len(transactions_df[transactions_df['transaction_type'] == 'SALE']) if not transactions_df.empty else 0
        st.metric(
            "Ümumi Satışlar", 
            total_sales,
            help="Ümumi satış əməliyyatlarının sayı"
        )
    
    # Diaqram Sırası
    col1, col2 = st.columns(2)
    
    with col1:
        # Stock levels chart (cached)
        fig_stock = generate_stock_chart(products_df)
        if fig_stock:
            st.plotly_chart(fig_stock, use_container_width=True)
    
    with col2:
        # Recent activity (cached)
        if not transactions_df.empty:
            fig_activity = generate_activity_chart(transactions_df)
            if fig_activity:
                st.plotly_chart(fig_activity, use_container_width=True)
        else:
            st.info("Hələlik heç bir əməliyyat yoxdur. Fəaliyyət görmək üçün satış və ya stok əlavəsi başladın.")

def show_sales_analytics_tab(products_df, transactions_df):
    """Satış analitikası və mənfəət analizi"""
    st.subheader("💰 Satış Analitikası")
    
    if transactions_df.empty:
        st.info("Satış məlumatı mövcud deyil. Analitika görmək üçün bəzi satışlar qeyd edin.")
        return
    
    # Filter for sales only
    sales_df = transactions_df[transactions_df['transaction_type'] == 'SALE'].copy()
    
    if sales_df.empty:
        st.info("Hələlik satış qeyd edilməyib. Satışları qeyd etmək üçün 'Stoku Yenilə' səhifəsindən istifadə edin.")
        return
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_items_sold = abs(sales_df['quantity_change'].sum())
    unique_products_sold = sales_df['product_id'].nunique()
    avg_sale_size = abs(sales_df['quantity_change'].mean())
    
    with col1:
        st.metric("Satılan Məhsullar", int(total_items_sold))
    
    with col2:
        st.metric("Satılan Məhsul Növləri", unique_products_sold)
    
    with col3:
        st.metric("Orta Satış Ölçüsü", f"{avg_sale_size:.1f}")
    
    with col4:
        # Calculate revenue (simplified - using current prices)
        revenue = 0
        for _, sale in sales_df.iterrows():
            product = products_df[products_df['product_id'] == sale['product_id']]
            if not product.empty:
                revenue += abs(sale['quantity_change']) * product.iloc[0]['price']
        st.metric("Təxmini Gəlir", format_currency(revenue))
    
    # Charts (cached)
    charts = generate_sales_charts(sales_df, products_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'top_selling' in charts:
            st.plotly_chart(charts['top_selling'], use_container_width=True)
    
    with col2:
        if 'trend' in charts:
            st.plotly_chart(charts['trend'], use_container_width=True)
        else:
            st.info("Tendensiya göstərmək üçün daha çox satış məlumatı lazımdır.")

def show_inventory_analysis_tab(products_df):
    """Anbar analizi və stok idarəetməsi məlumatları"""
    st.subheader("📦 Anbar Analizi")
    
    # Stock status overview
    col1, col2, col3 = st.columns(3)
    
    low_stock = products_df[products_df['quantity'] <= products_df['min_quantity']]
    out_of_stock = products_df[products_df['quantity'] == 0]
    overstocked = products_df[products_df['quantity'] > products_df['min_quantity'] * 3]
    
    with col1:
        st.metric(
            "Az Stok", 
            len(low_stock),
            delta=f"-{len(low_stock)}" if len(low_stock) > 0 else "0",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Stokda Yoxdur", 
            len(out_of_stock),
            delta=f"-{len(out_of_stock)}" if len(out_of_stock) > 0 else "0",
            delta_color="inverse"
        )
    
    with col3:
        st.metric("Yaxşı Stoklanmış", len(overstocked))
    
    # Charts (cached)
    charts = generate_inventory_charts(products_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'distribution' in charts:
            st.plotly_chart(charts['distribution'], use_container_width=True)
    
    with col2:
        if 'value' in charts:
            st.plotly_chart(charts['value'], use_container_width=True)
    
    # Detailed stock status table
    st.subheader("🔍 Ətraflı Stok Vəziyyəti")
    
    # Create status column
    def get_stock_status(row):
        if row['quantity'] == 0:
            return "🔴 Stokda Yoxdur"
        elif row['quantity'] <= row['min_quantity']:
            return "🟡 Az Stok"
        elif row['quantity'] <= row['min_quantity'] * 2:
            return "🟢 Normal"
        else:
            return "🔵 Yüksək Stok"
    
    display_df = products_df.copy()
    display_df['Vəziyyət'] = display_df.apply(get_stock_status, axis=1)
    display_df['Dəyər'] = display_df.apply(lambda x: format_currency(x['quantity'] * x['price']), axis=1)
    
    # Select columns for display
    status_df = display_df[['name', 'quantity', 'min_quantity', 'Vəziyyət', 'Dəyər']].copy()
    status_df.columns = ['Məhsul', 'Hazırki Stok', 'Min Stok', 'Vəziyyət', 'Ümumi Dəyər']
    
    st.dataframe(status_df, use_container_width=True)

def show_reports_tab(products_df, transactions_df):
    """Hesabatlar və ixrac funksionallığı"""
    st.subheader("📋 Hesabatlar və İxrac")
    
    # Report options
    report_type = st.selectbox(
        "Hesabat Növünü Seçin",
        ["Anbar Xülasəsi", "Satış Hesabatı", "Az Stok Hesabatı", "Əməliyyat Tarixçəsi"]
    )
    
    if report_type == "Anbar Xülasəsi":
        st.subheader("📦 Anbar Xülasəsi Hesabatı")
        
        # Summary stats
        total_items = int(products_df['quantity'].sum())
        total_value = (products_df['quantity'] * products_df['price']).sum()
        avg_price = products_df['price'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ümumi Məhsullar", total_items)
        with col2:
            st.metric("Ümumi Dəyər", format_currency(total_value))
        with col3:
            st.metric("Orta Qiymət", format_currency(avg_price))
        
        # Detailed table
        report_df = products_df.copy()
        report_df['Ümumi Dəyər'] = report_df['quantity'] * report_df['price']
        report_df = report_df[['name', 'quantity', 'min_quantity', 'price', 'Ümumi Dəyər']]
        report_df.columns = ['Məhsul', 'Stok', 'Min Stok', 'Qiymət', 'Ümumi Dəyər']
        
        st.dataframe(report_df, use_container_width=True)
        
        # Export button
        csv = report_df.to_csv(index=False)
        st.download_button(
            label="📥 Anbar Hesabatını Yüklə (CSV)",
            data=csv,
            file_name=f"anbar_hesabati_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    elif report_type == "Satış Hesabatı" and not transactions_df.empty:
        st.subheader("💰 Satış Hesabatı")
        
        sales_df = transactions_df[transactions_df['transaction_type'] == 'SALE'].copy()
        
        if not sales_df.empty:
            # Summary
            total_sales = len(sales_df)
            total_items_sold = abs(sales_df['quantity_change'].sum())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Ümumi Satışlar", total_sales)
            with col2:
                st.metric("Satılan Məhsullar", int(total_items_sold))
            
            # Detailed sales
            sales_report = sales_df[['product_name', 'quantity_change', 'timestamp']].copy()
            sales_report['quantity_change'] = abs(sales_report['quantity_change'])
            sales_report.columns = ['Məhsul', 'Satılan Miqdar', 'Tarix']
            
            st.dataframe(sales_report, use_container_width=True)
            
            # Export
            csv = sales_report.to_csv(index=False)
            st.download_button(
                label="📥 Satış Hesabatını Yüklə (CSV)",
                data=csv,
                file_name=f"satis_hesabati_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("Hələlik satış qeyd edilməyib.")
    
    elif report_type == "Az Stok Hesabatı":
        st.subheader("⚠️ Az Stok Hesabatı")
        
        low_stock_df = products_df[products_df['quantity'] <= products_df['min_quantity']].copy()
        
        if not low_stock_df.empty:
            low_stock_report = low_stock_df[['name', 'quantity', 'min_quantity', 'price']].copy()
            low_stock_report.columns = ['Məhsul', 'Hazırki Stok', 'Min Stok', 'Qiymət']
            
            st.dataframe(low_stock_report, use_container_width=True)
            
            # Export
            csv = low_stock_report.to_csv(index=False)
            st.download_button(
                label="📥 Az Stok Hesabatını Yüklə (CSV)",
                data=csv,
                file_name=f"az_stok_hesabati_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ Az stoklu məhsul yoxdur!")
    
    elif report_type == "Əməliyyat Tarixçəsi" and not transactions_df.empty:
        st.subheader("📋 Əməliyyat Tarixçəsi")
        
        # Date filter
        if not transactions_df.empty:
            transactions_df['date'] = pd.to_datetime(transactions_df['timestamp']).dt.date
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Başlanğıc Tarixi", value=transactions_df['date'].min())
            with col2:
                end_date = st.date_input("Bitmə Tarixi", value=transactions_df['date'].max())
            
            # Filter transactions
            filtered_df = transactions_df[
                (transactions_df['date'] >= start_date) & 
                (transactions_df['date'] <= end_date)
            ].copy()
            
            if not filtered_df.empty:
                history_report = filtered_df[['product_name', 'transaction_type', 'quantity_change', 'timestamp']].copy()
                history_report['transaction_type'] = history_report['transaction_type'].apply(
                    lambda x: 'Satış' if x == 'SALE' else 'Stok Əlavəsi'
                )
                history_report.columns = ['Məhsul', 'Növ', 'Miqdar Dəyişikliyi', 'Tarix']
                
                st.dataframe(history_report, use_container_width=True)
                
                # Export
                csv = history_report.to_csv(index=False)
                st.download_button(
                    label="📥 Əməliyyat Tarixçəsini Yüklə (CSV)",
                    data=csv,
                    file_name=f"emeliyyat_tarixcesi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("Seçilmiş tarix aralığında heç bir əməliyyat yoxdur.")
        else:
            st.info("Hələlik heç bir əməliyyat qeyd edilməyib.")

if __name__ == "__main__":
    show_dashboard_page()