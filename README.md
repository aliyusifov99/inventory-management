# Inventory Management System - Project Structure

```
inventory_management/
│
├── app.py                          # Main Streamlit application entry point
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── .gitignore                      # Git ignore file
├── .env.example                    # Environment variables template
│
├── config/
│   ├── __init__.py
│   ├── database.py                 # Database configuration and connection
│   └── settings.py                 # App settings and constants
│
├── database/
│   ├── __init__.py
│   ├── models.py                   # Database models/schema
│   ├── operations.py               # Database CRUD operations
│   └── migrations/                 # Database migration scripts (future)
│       └── __init__.py
│
├── pages/
│   ├── __init__.py
│   ├── add_product.py              # Add product page
│   ├── view_products.py            # View products page
│   ├── update_stock.py             # Update stock page (Phase 2)
│   ├── transactions.py             # Transaction history page (Phase 3)
│   └── dashboard.py                # Dashboard page (Phase 4)
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py                  # Helper functions
│   ├── validation.py               # Input validation functions
│   └── backup.py                   # Backup utilities (Phase 6)
│
├── static/
│   ├── css/
│   │   └── style.css               # Custom CSS (if needed)
│   └── images/
│       └── logo.png                # App logo/images
│
├── data/
│   └── inventory.db                # SQLite database file (gitignored)
│
├── backups/                        # Local backups folder (gitignored)
│
└── tests/
    ├── __init__.py
    ├── test_database.py            # Database tests
    ├── test_operations.py          # Operations tests
    └── test_utils.py               # Utility function tests
```

## File Contents Overview

### Root Files

**app.py** - Main application entry point
```python
# Main Streamlit app with navigation and page routing
```

**requirements.txt**
```
streamlit
pandas
sqlite3  # Built into Python
python-dotenv
plotly  # For charts in Phase 4
```

**README.md** - Project documentation with setup instructions

**.gitignore**
```
*.db
.env
__pycache__/
*.pyc
.streamlit/
backups/
.DS_Store
```

### Config Module
- **database.py** - Database connection and configuration
- **settings.py** - App constants, database paths, etc.

### Database Module
- **models.py** - Database schema definitions
- **operations.py** - All CRUD operations (add_product, get_products, etc.)

### Pages Module
- Each page as a separate module for better organization
- Easy to maintain and extend

### Utils Module
- **helpers.py** - Common utility functions
- **validation.py** - Input validation logic
- **backup.py** - Backup functionality (Phase 6)

## Phase-by-Phase Implementation

**Phase 1 Files to Create:**
```
app.py
requirements.txt
config/database.py
config/settings.py
database/models.py
database/operations.py
pages/add_product.py
pages/view_products.py
utils/helpers.py
utils/validation.py
```

**Phase 2 Addition:**
```
pages/update_stock.py
```

**Phase 3 Addition:**
```
pages/transactions.py
```

**Phase 4 Addition:**
```
pages/dashboard.py
```

**Phase 5 (Cloud Migration):**
- Update config/database.py for PlanetScale
- Add .env file for database credentials

**Phase 6 Addition:**
```
utils/backup.py
```
