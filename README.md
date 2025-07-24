# 📦 Inventory Management System

A modern and user-friendly inventory management system built with Streamlit, featuring full functionality with SQLite and PostgreSQL support.

## ✨ Features

### 🏪 Product Management
- ➕ Add new products with detailed information
- 📋 View all products in an organized table
- ✏️ Edit product details and pricing
- 🗑️ Delete products with confirmation
- 🔍 Search products by name (case-insensitive)

### 📊 Stock Management
- 📈 Update stock levels with transaction tracking
- 💰 Record sales and restocking operations
- ⚠️ Automatic low stock alerts and warnings
- 📋 Complete transaction history for each product
- 🔄 Real-time stock level updates

### 📈 Analytics & Reports
- 📊 Interactive dashboard with key metrics
- 💹 Sales analytics with trend visualization
- 📦 Inventory analysis and distribution charts
- 📥 Export reports to CSV format
- 📈 Visual charts with Plotly integration

### ⚡ Performance Features
- 🚀 Smart caching system for optimal performance
- 🔄 Automatic cache invalidation on data changes
- 📱 Mobile-responsive design
- 🎨 Modern and intuitive user interface

## 🚀 Live Demo

🌐 **[View Live Demo](https://your-app-url.streamlit.app)** - Try the application

## 🛠️ Technologies

- **Backend**: Python 3.9+
- **Web Framework**: Streamlit
- **Database**: SQLite (local) / PostgreSQL (cloud)
- **Visualization**: Plotly
- **Data Analysis**: Pandas
- **ORM**: SQLAlchemy
- **Deployment**: Streamlit Cloud

## 📁 Project Structure

```
inventory-management/
├── app.py                 # Main application entry point
├── config/
│   ├── __init__.py
│   ├── database.py        # Database configuration and connections
│   └── settings.py        # Application settings and environment variables
├── database/
│   ├── __init__.py
│   └── operations.py      # Database operations with caching
├── pages/
│   ├── __init__.py
│   ├── dashboard.py       # Analytics dashboard
│   ├── add_product.py     # Add new products
│   ├── view_products.py   # View and manage products
│   └── update_stock.py    # Stock management
├── utils/
│   ├── __init__.py
│   └── validation.py      # Input validation and formatting
├── data/
│   └── inventory.db       # SQLite database (local development)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## ⚡ Quick Start

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/inventory-management.git
cd inventory-management
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Create a `.env` file in the root directory:

```env
# For SQLite (Local Development) - Default
DB_TYPE=sqlite

# For PostgreSQL (Production with Supabase)
# DB_TYPE=postgres
# SUPABASE_HOST=db.your-project.supabase.co
# SUPABASE_PORT=5432
# SUPABASE_DATABASE=postgres
# SUPABASE_USER=postgres
# SUPABASE_PASSWORD=your-password
```

### 5️⃣ Run the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

## 🌐 Streamlit Cloud Deployment

### 1️⃣ Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2️⃣ Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Select your repository and set main file to `app.py`
4. Add your environment variables in the Secrets section

### 3️⃣ Configure Secrets

In Streamlit Cloud Advanced settings → Secrets:

```toml
# For SQLite (Simple setup)
DB_TYPE = "sqlite"

# For PostgreSQL (Production setup)
# DB_TYPE = "postgres"
# SUPABASE_HOST = "db.your-project.supabase.co"
# SUPABASE_PORT = "5432"
# SUPABASE_DATABASE = "postgres"
# SUPABASE_USER = "postgres"
# SUPABASE_PASSWORD = "your-secure-password"
```

## 💾 Database Options

### 🗄️ SQLite (Recommended for Local Development)
- **Pros**: Easy setup, no configuration required, lightweight
- **Cons**: Single-user, limited scalability
- **Best for**: Development, testing, small-scale deployments

### 🐘 PostgreSQL with Supabase (Recommended for Production)
- **Pros**: Scalable, multi-user support, cloud-hosted, robust
- **Cons**: Requires setup and configuration
- **Best for**: Production environments, multiple users

## 🎯 Usage Guide

### 📦 Adding Products

1. Navigate to **"Add Product"** page
2. Fill in the product information:
   - **Product Name** (required): Unique product identifier
   - **Current Quantity**: Initial stock level
   - **Minimum Quantity**: Reorder alert threshold
   - **Selling Price** (required): Customer price
   - **Purchase Cost**: For profit calculation
3. Click **"Add Product"** to save

### 📊 Managing Stock

1. Go to **"Update Stock"** page
2. Select a product from the dropdown
3. Choose transaction type:
   - **SALE**: Reduces stock (for customer purchases)
   - **RESTOCK**: Increases stock (for new inventory)
4. Enter quantity and confirm the transaction

### 📈 Viewing Analytics

Access the **"Dashboard"** to see:
- 📊 **Overview**: Key metrics and recent activity
- 💰 **Sales Analytics**: Sales trends and top products
- 📦 **Inventory Analysis**: Stock distribution and value analysis
- 📋 **Reports**: Exportable CSV reports

### 🔍 Searching and Filtering

- Use the search bar on **"View Products"** page
- Search is case-insensitive and matches partial names
- Sort products by different columns
- Filter by stock status (low stock alerts)

## ⚡ Performance Optimization

### 🚀 Caching System

The application implements intelligent caching for optimal performance:

- **Data Caching**: Database queries cached for 1-5 minutes
- **Chart Caching**: Visualization generation cached for 2-5 minutes
- **Automatic Invalidation**: Cache cleared when data changes
- **Manual Refresh**: 🔄 button to force cache refresh

### 📊 Cache Strategy

```python
@st.cache_data(ttl=60)    # 1 minute - frequently changing data
@st.cache_data(ttl=300)   # 5 minutes - stable data
```

**Cache TTL (Time To Live) by Function:**
- Products list: 1 minute
- Inventory stats: 5 minutes
- Transactions: 1 minute
- Charts: 2-5 minutes

## 🛡️ Security Features

- ✅ **SQL Injection Protection**: Parameterized queries
- ✅ **Input Validation**: Server-side data validation
- ✅ **Error Handling**: Graceful error management
- ✅ **Environment Variables**: Secure credential storage
- ✅ **Data Sanitization**: Clean user inputs

## 📱 User Interface

### 🎨 Design Features
- **Responsive Design**: Works on desktop and mobile
- **Modern UI**: Clean and intuitive interface
- **Interactive Charts**: Plotly-powered visualizations
- **Real-time Updates**: Live data refresh
- **Loading Indicators**: User feedback during operations

### 🌟 User Experience
- **Smart Navigation**: Easy page switching
- **Form Validation**: Real-time input feedback
- **Success Animations**: Celebratory effects
- **Error Handling**: Clear error messages
- **Help Documentation**: Built-in usage guides

## 📊 Analytics Features

### 📈 Dashboard Metrics
- Total products count
- Inventory value calculation
- Low stock alerts
- Sales transaction count

### 💹 Sales Analytics
- Revenue estimation
- Top-selling products
- Sales trends over time
- Average sale size

### 📦 Inventory Analysis
- Stock level distribution
- High-value inventory items
- Out-of-stock products
- Well-stocked items

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📋 Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Include error handling
- Update tests if applicable
- Update documentation

## 🐛 Bug Reports

Found a bug? Please create an issue on [GitHub Issues](https://github.com/yourusername/inventory-management/issues) with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- System information (OS, Python version, browser)

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) - Amazing web app framework
- [Plotly](https://plotly.com/) - Interactive visualization library
- [Pandas](https://pandas.pydata.org/) - Powerful data manipulation
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Supabase](https://supabase.com/) - Open source Firebase alternative



⭐ **If you found this project helpful, please give it a star on GitHub!**

🚀 **Ready to manage your inventory efficiently? [Get started now!](#quick-start)**