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

def show_dashboard_page():
    """Display the advanced dashboard page"""
    st.header("📊 Dashboard & Analytics")
    
    # Get data
    products_df = get_all_products()
    transactions_df = get_all_transactions()
    stats = get_inventory_stats()
    
    if products_df.empty:
        st.info("No data available. Add some products to see analytics.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "💰 Sales Analytics", "📦 Inventory Analysis", "📋 Reports"])
    
    with tab1:
        show_overview_tab(products_df, transactions_df, stats)
    
    with tab2:
        show_sales_analytics_tab(products_df, transactions_df)
    
    with tab3:
        show_inventory_analysis_tab(products_df)
    
    with tab4:
        show_reports_tab(products_df, transactions_df)

def show_overview_tab(products_df, transactions_df, stats):
    """Overview dashboard with key metrics"""
    st.subheader("📈 Business Overview")
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Products", 
            stats['total_products'],
            help="Total number of unique products"
        )
    
    with col2:
        st.metric(
            "Stock Value", 
            format_currency(stats['total_value']),
            help="Total value of current inventory"
        )
    
    with col3:
        st.metric(
            "Low Stock Items", 
            stats['low_stock_count'],
            delta=f"-{stats['low_stock_count']}" if stats['low_stock_count'] > 0 else "0",
            delta_color="inverse",
            help="Products at or below minimum level"
        )
    
    with col4:
        total_sales = len(transactions_df[transactions_df['transaction_type'] == 'SALE']) if not transactions_df.empty else 0
        st.metric(
            "Total Sales", 
            total_sales,
            help="Total number of sales transactions"
        )
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        # Stock levels chart
        if not products_df.empty:
            fig_stock = px.bar(
                products_df.head(10), 
                x='name', 
                y='quantity',
                title='📦 Current Stock Levels (Top 10)',
                color='quantity',
                color_continuous_scale='RdYlGn'
            )
            fig_stock.update_xaxes(title="Product", tickangle=45)
            fig_stock.update_yaxes(title="Quantity")
            fig_stock.update_layout(height=400)
            st.plotly_chart(fig_stock, use_container_width=True)
    
    with col2:
        # Recent activity
        if not transactions_df.empty:
            # Process recent transactions
            recent_transactions = transactions_df.head(7)
            recent_transactions['date'] = pd.to_datetime(recent_transactions['timestamp']).dt.date
            daily_activity = recent_transactions.groupby(['date', 'transaction_type']).size().reset_index(name='count')
            
            fig_activity = px.bar(
                daily_activity,
                x='date',
                y='count',
                color='transaction_type',
                title='📅 Recent Activity (Last 7 Days)',
                color_discrete_map={'SALE': '#ff6b6b', 'RESTOCK': '#51cf66'}
            )
            fig_activity.update_xaxes(title="Date")
            fig_activity.update_yaxes(title="Number of Transactions")
            fig_activity.update_layout(height=400)
            st.plotly_chart(fig_activity, use_container_width=True)
        else:
            st.info("No transactions yet. Start selling or restocking to see activity.")

def show_sales_analytics_tab(products_df, transactions_df):
    """Sales analytics and profit analysis"""
    st.subheader("💰 Sales Analytics")
    
    if transactions_df.empty:
        st.info("No sales data available. Record some sales to see analytics.")
        return
    
    # Filter for sales only
    sales_df = transactions_df[transactions_df['transaction_type'] == 'SALE'].copy()
    
    if sales_df.empty:
        st.info("No sales recorded yet. Use 'Update Stock' to record sales.")
        return
    
    # Sales metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_items_sold = abs(sales_df['quantity_change'].sum())
    unique_products_sold = sales_df['product_id'].nunique()
    avg_sale_size = abs(sales_df['quantity_change'].mean())
    
    with col1:
        st.metric("Items Sold", int(total_items_sold))
    
    with col2:
        st.metric("Products Sold", unique_products_sold)
    
    with col3:
        st.metric("Avg Sale Size", f"{avg_sale_size:.1f}")
    
    with col4:
        # Calculate revenue (simplified - using current prices)
        revenue = 0
        for _, sale in sales_df.iterrows():
            product = products_df[products_df['product_id'] == sale['product_id']]
            if not product.empty:
                revenue += abs(sale['quantity_change']) * product.iloc[0]['price']
        st.metric("Est. Revenue", format_currency(revenue))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top selling products
        product_sales = sales_df.groupby('product_name')['quantity_change'].apply(lambda x: abs(x).sum()).reset_index()
        product_sales = product_sales.sort_values('quantity_change', ascending=False).head(10)
        
        if not product_sales.empty:
            fig_top = px.bar(
                product_sales,
                x='quantity_change',
                y='product_name',
                orientation='h',
                title='🏆 Top Selling Products',
                color='quantity_change',
                color_continuous_scale='Blues'
            )
            fig_top.update_xaxes(title="Units Sold")
            fig_top.update_yaxes(title="Product")
            fig_top.update_layout(height=400)
            st.plotly_chart(fig_top, use_container_width=True)
    
    with col2:
        # Sales over time
        sales_df['date'] = pd.to_datetime(sales_df['timestamp']).dt.date
        daily_sales = sales_df.groupby('date')['quantity_change'].apply(lambda x: abs(x).sum()).reset_index()
        
        if len(daily_sales) > 1:
            fig_trend = px.line(
                daily_sales,
                x='date',
                y='quantity_change',
                title='📈 Sales Trend',
                markers=True
            )
            fig_trend.update_xaxes(title="Date")
            fig_trend.update_yaxes(title="Items Sold")
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("Need more sales data to show trends.")

def show_inventory_analysis_tab(products_df):
    """Inventory analysis and stock management insights"""
    st.subheader("📦 Inventory Analysis")
    
    # Stock status overview
    col1, col2, col3 = st.columns(3)
    
    low_stock = products_df[products_df['quantity'] <= products_df['min_quantity']]
    out_of_stock = products_df[products_df['quantity'] == 0]
    overstocked = products_df[products_df['quantity'] > products_df['min_quantity'] * 3]  # More than 3x minimum
    
    with col1:
        st.metric(
            "Low Stock", 
            len(low_stock),
            delta=f"-{len(low_stock)}" if len(low_stock) > 0 else "0",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "Out of Stock", 
            len(out_of_stock),
            delta=f"-{len(out_of_stock)}" if len(out_of_stock) > 0 else "0",
            delta_color="inverse"
        )
    
    with col3:
        st.metric("Well Stocked", len(overstocked))
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Stock distribution
        stock_ranges = []
        labels = []
        
        for _, product in products_df.iterrows():
            qty = product['quantity']
            min_qty = product['min_quantity']
            
            if qty == 0:
                stock_ranges.append('Out of Stock')
            elif qty <= min_qty:
                stock_ranges.append('Low Stock')
            elif qty <= min_qty * 2:
                stock_ranges.append('Normal Stock')
            else:
                stock_ranges.append('High Stock')
        
        stock_dist = pd.Series(stock_ranges).value_counts()
        
        fig_dist = px.pie(
            values=stock_dist.values,
            names=stock_dist.index,
            title='📊 Stock Level Distribution',
            color_discrete_map={
                'Out of Stock': '#ff6b6b',
                'Low Stock': '#feca57',
                'Normal Stock': '#48dbfb',
                'High Stock': '#1dd1a1'
            }
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)
    
    with col2:
        # Value analysis
        products_df['total_value'] = products_df['quantity'] * products_df['price']
        top_value = products_df.nlargest(10, 'total_value')
        
        fig_value = px.bar(
            top_value,
            x='total_value',
            y='name',
            orientation='h',
            title='💎 Highest Value Inventory',
            color='total_value',
            color_continuous_scale='Greens'
        )
        fig_value.update_xaxes(title="Total Value ($)")
        fig_value.update_yaxes(title="Product")
        fig_value.update_layout(height=400)
        st.plotly_chart(fig_value, use_container_width=True)
    
    # Detailed stock status table
    st.subheader("🔍 Detailed Stock Status")
    
    # Create status column
    def get_stock_status(row):
        if row['quantity'] == 0:
            return "🔴 Out of Stock"
        elif row['quantity'] <= row['min_quantity']:
            return "🟡 Low Stock"
        elif row['quantity'] <= row['min_quantity'] * 2:
            return "🟢 Normal"
        else:
            return "🔵 High Stock"
    
    display_df = products_df.copy()
    display_df['Status'] = display_df.apply(get_stock_status, axis=1)
    display_df['Value'] = display_df.apply(lambda x: format_currency(x['quantity'] * x['price']), axis=1)
    
    # Select columns for display
    status_df = display_df[['name', 'quantity', 'min_quantity', 'Status', 'Value']].copy()
    status_df.columns = ['Product', 'Current Stock', 'Min Stock', 'Status', 'Total Value']
    
    st.dataframe(status_df, use_container_width=True)

def show_reports_tab(products_df, transactions_df):
    """Reports and export functionality"""
    st.subheader("📋 Reports & Export")
    
    # Report options
    report_type = st.selectbox(
        "Select Report Type",
        ["Inventory Summary", "Sales Report", "Low Stock Report", "Transaction History"]
    )
    
    if report_type == "Inventory Summary":
        st.subheader("📦 Inventory Summary Report")
        
        # Summary stats
        total_items = int(products_df['quantity'].sum())
        total_value = (products_df['quantity'] * products_df['price']).sum()
        avg_price = products_df['price'].mean()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", total_items)
        with col2:
            st.metric("Total Value", format_currency(total_value))
        with col3:
            st.metric("Avg Price", format_currency(avg_price))
        
        # Detailed table
        report_df = products_df.copy()
        report_df['Total Value'] = report_df['quantity'] * report_df['price']
        report_df = report_df[['name', 'quantity', 'min_quantity', 'price', 'Total Value']]
        report_df.columns = ['Product', 'Stock', 'Min Stock', 'Price', 'Total Value']
        
        st.dataframe(report_df, use_container_width=True)
        
        # Export button
        csv = report_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Inventory Report (CSV)",
            data=csv,
            file_name=f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    elif report_type == "Sales Report" and not transactions_df.empty:
        st.subheader("💰 Sales Report")
        
        sales_df = transactions_df[transactions_df['transaction_type'] == 'SALE'].copy()
        
        if not sales_df.empty:
            # Summary
            total_sales = len(sales_df)
            total_items_sold = abs(sales_df['quantity_change'].sum())
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Sales", total_sales)
            with col2:
                st.metric("Items Sold", int(total_items_sold))
            
            # Detailed sales
            sales_report = sales_df[['product_name', 'quantity_change', 'timestamp']].copy()
            sales_report['quantity_change'] = abs(sales_report['quantity_change'])
            sales_report.columns = ['Product', 'Quantity Sold', 'Date']
            
            st.dataframe(sales_report, use_container_width=True)
            
            # Export
            csv = sales_report.to_csv(index=False)
            st.download_button(
                label="📥 Download Sales Report (CSV)",
                data=csv,
                file_name=f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No sales recorded yet.")
    
    elif report_type == "Low Stock Report":
        st.subheader("⚠️ Low Stock Report")
        
        low_stock_df = products_df[products_df['quantity'] <= products_df['min_quantity']].copy()
        
        if not low_stock_df.empty:
            low_stock_report = low_stock_df[['name', 'quantity', 'min_quantity', 'price']].copy()
            low_stock_report.columns = ['Product', 'Current Stock', 'Min Stock', 'Price']
            
            st.dataframe(low_stock_report, use_container_width=True)
            
            # Export
            csv = low_stock_report.to_csv(index=False)
            st.download_button(
                label="📥 Download Low Stock Report (CSV)",
                data=csv,
                file_name=f"low_stock_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.success("✅ No low stock items!")
    
    elif report_type == "Transaction History" and not transactions_df.empty:
        st.subheader("📋 Transaction History")
        
        # Date filter
        if not transactions_df.empty:
            transactions_df['date'] = pd.to_datetime(transactions_df['timestamp']).dt.date
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From Date", value=transactions_df['date'].min())
            with col2:
                end_date = st.date_input("To Date", value=transactions_df['date'].max())
            
            # Filter transactions
            filtered_df = transactions_df[
                (transactions_df['date'] >= start_date) & 
                (transactions_df['date'] <= end_date)
            ].copy()
            
            if not filtered_df.empty:
                history_report = filtered_df[['product_name', 'transaction_type', 'quantity_change', 'timestamp']].copy()
                history_report.columns = ['Product', 'Type', 'Quantity Change', 'Date']
                
                st.dataframe(history_report, use_container_width=True)
                
                # Export
                csv = history_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download Transaction History (CSV)",
                    data=csv,
                    file_name=f"transaction_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No transactions in selected date range.")
        else:
            st.info("No transactions recorded yet.")

if __name__ == "__main__":
    show_dashboard_page()