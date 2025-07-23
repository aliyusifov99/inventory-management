# utils/validation.py

def validate_product_data(name, price, quantity=None, min_quantity=None, cost=None):
    """Validate product input data"""
    errors = []
    
    # Name validation
    if not name or not name.strip():
        errors.append("Product name is required")
    elif len(name.strip()) < 2:
        errors.append("Product name must be at least 2 characters long")
    
    # Price validation
    if price is None or price <= 0:
        errors.append("Price must be greater than 0")
    
    # Quantity validation (optional)
    if quantity is not None and quantity < 0:
        errors.append("Quantity cannot be negative")
    
    # Minimum quantity validation (optional)
    if min_quantity is not None and min_quantity < 0:
        errors.append("Minimum quantity cannot be negative")
    
    # Cost validation (optional)
    if cost is not None and cost < 0:
        errors.append("Cost cannot be negative")
    
    return errors

def is_valid_product_name(name):
    """Check if product name is valid"""
    return name and name.strip() and len(name.strip()) >= 2

def is_valid_price(price):
    """Check if price is valid"""
    return price is not None and price > 0

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:.2f}"