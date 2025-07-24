# utils/validation.py

def validate_product_data(name, price, quantity=None, min_quantity=None, cost=None):
    """Məhsul giriş məlumatlarını yoxla"""
    errors = []
    
    # Ad yoxlanması
    if not name or not name.strip():
        errors.append("Məhsul adı tələb olunur")
    elif len(name.strip()) < 2:
        errors.append("Məhsul adı ən azı 2 simvol olmalıdır")
    
    # Qiymət yoxlanması
    if price is None or price <= 0:
        errors.append("Qiymət 0-dan böyük olmalıdır")
    
    # Miqdar yoxlanması (istəyə bağlı)
    if quantity is not None and quantity < 0:
        errors.append("Miqdar mənfi ola bilməz")
    
    # Minimum miqdar yoxlanması (istəyə bağlı)
    if min_quantity is not None and min_quantity < 0:
        errors.append("Minimum miqdar mənfi ola bilməz")
    
    # Maya dəyəri yoxlanması (istəyə bağlı)
    if cost is not None and cost < 0:
        errors.append("Maya dəyəri mənfi ola bilməz")
    
    return errors

def is_valid_product_name(name):
    """Məhsul adının keçərli olub olmadığını yoxla"""
    return name and name.strip() and len(name.strip()) >= 2

def is_valid_price(price):
    """Qiymətin keçərli olub olmadığını yoxla"""
    return price is not None and price > 0

def format_currency(amount):
    """Məbləği valyuta kimi formatla"""
    return f"₼{amount:.2f}"