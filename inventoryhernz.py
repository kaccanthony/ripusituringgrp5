import json
import datetime
import os

# ============================================
# FEATURE 1: SALES TRANSACTION SYSTEM
# ============================================

class SalesTransaction:
    """Represents a single sales transaction"""
    
    def __init__(self, transaction_id, product_id, product_name, quantity, price_per_unit, total_amount, date=None):
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.total_amount = total_amount
        self.date = date if date else datetime.datetime.now()
    
    def to_dict(self):
        """Convert transaction to dictionary for JSON storage"""
        return {
            'transaction_id': self.transaction_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
            'total_amount': self.total_amount,
            'date': self.date.isoformat()
        }
    
    def display(self):
        """Display transaction details"""
        print(f"ID: {self.transaction_id} | Product: {self.product_name} | "
              f"Qty: {self.quantity} | Total: ${self.total_amount:.2f} | "
              f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}")


class SalesManager:
    """Manages all sales transactions"""
    
    def __init__(self, sales_file='sales_data.json'):
        self.sales_file = sales_file
        self.transactions = []
        self.next_id = 1
        self.load_transactions()
    
    def load_transactions(self):
        """Load sales history from file"""
        if os.path.exists(self.sales_file):
            try:
                with open(self.sales_file, 'r') as f:
                    data = json.load(f)
                    self.transactions = [SalesTransaction(
                        t['transaction_id'],
                        t['product_id'],
                        t['product_name'],
                        t['quantity'],
                        t['price_per_unit'],
                        t['total_amount'],
                        datetime.datetime.fromisoformat(t['date'])
                    ) for t in data.get('transactions', [])]
                    self.next_id = data.get('next_id', 1)
                print(f"✓ Loaded {len(self.transactions)} sales records")
            except:
                print("! No sales data found, starting fresh")
    
    def save_transactions(self):
        """Save sales history to file"""
        with open(self.sales_file, 'w') as f:
            json.dump({
                'transactions': [t.to_dict() for t in self.transactions],
                'next_id': self.next_id
            }, f, indent=4)
    
    def record_sale(self, product_id, product_name, quantity, price_per_unit, current_stock):
        """
        Record a sale transaction
        Returns: (success, message, transaction_object)
        """
        # Validation
        if quantity <= 0:
            return False, "Quantity must be greater than zero", None
        
        if current_stock < quantity:
            return False, f"Insufficient stock! Only {current_stock} units available", None
        
        # Calculate total
        total_amount = quantity * price_per_unit
        
        # Create transaction
        transaction = SalesTransaction(
            self.next_id,
            product_id,
            product_name,
            quantity,
            price_per_unit,
            total_amount
        )
        
        # Save transaction
        self.transactions.append(transaction)
        self.next_id += 1
        self.save_transactions()
        
        return True, f"Sale recorded successfully! Total: ${total_amount:.2f}", transaction
    
    def get_sales_history(self, limit=None):
        """Get sales history, optionally limited to last N transactions"""
        sorted_transactions = sorted(self.transactions, key=lambda x: x.date, reverse=True)
        if limit:
            return sorted_transactions[:limit]
        return sorted_transactions
    
    def get_total_revenue(self):
        """Calculate total revenue from all sales"""
        return sum(t.total_amount for t in self.transactions)
    
    def display_sales_history(self, limit=20):
        """Display sales history in a formatted table"""
        if not self.transactions:
            print("\n📭 No sales transactions found")
            return
        
        history = self.get_sales_history(limit)
        
        print("\n" + "="*80)
        print("SALES HISTORY".center(80))
        print("="*80)
        print(f"{'ID':<6} {'Product':<20} {'Qty':<6} {'Unit Price':<12} {'Total':<12} {'Date':<20}")
        print("-"*80)
        
        for t in history:
            print(f"{t.transaction_id:<6} {t.product_name:<20} {t.quantity:<6} "
                  f"${t.price_per_unit:<11.2f} ${t.total_amount:<11.2f} "
                  f"{t.date.strftime('%Y-%m-%d %H:%M')}")
        
        print("-"*80)
        print(f"Total Revenue: ${self.get_total_revenue():.2f}")
        if len(self.transactions) > limit:
            print(f"\n(Showing last {limit} of {len(self.transactions)} transactions)")


# ============================================
# FEATURE 2: LOW STOCK ALERT SYSTEM
# ============================================

class LowStockAlert:
    """Generates and manages low stock alerts"""
    
    def __init__(self, threshold=5):
        """
        Initialize alert system
        threshold: minimum stock level before triggering alert (default 5)
        """
        self.threshold = threshold
    
    def check_product_stock(self, product_id, product_name, current_stock):
        """
        Check if a single product is below threshold
        Returns: (is_low, alert_message, severity)
        """
        if current_stock <= 0:
            return True, f"⚠️ CRITICAL: {product_name} (ID: {product_id}) is OUT OF STOCK!", "CRITICAL"
        elif current_stock <= self.threshold:
            return True, f"⚠️ LOW STOCK: {product_name} (ID: {product_id}) only has {current_stock} units left (Threshold: {self.threshold})", "LOW"
        return False, "", "OK"
    
    def get_low_stock_products(self, products_dict):
        """
        Check all products for low stock
        products_dict: dictionary of product objects with 'stock' attribute
        
        Returns: list of (product_id, product_name, current_stock, severity)
        """
        low_stock_items = []
        
        for product_id, product in products_dict.items():
            is_low, _, severity = self.check_product_stock(
                product_id, 
                getattr(product, 'name', 'Unknown'), 
                getattr(product, 'stock', 0)
            )
            if is_low:
                low_stock_items.append({
                    'id': product_id,
                    'name': getattr(product, 'name', 'Unknown'),
                    'stock': getattr(product, 'stock', 0),
                    'severity': severity
                })
        
        return low_stock_items
    
    def display_alerts(self, products_dict):
        """Display all low stock alerts in a formatted way"""
        low_stock_items = self.get_low_stock_products(products_dict)
        
        if not low_stock_items:
            print("\n✅ All products have sufficient stock (above threshold of {})".format(self.threshold))
            return
        
        print("\n" + "="*70)
        print("⚠️ LOW STOCK ALERTS ⚠️".center(70))
        print("="*70)
        print(f"{'Severity':<12} {'Product ID':<15} {'Product Name':<25} {'Current Stock':<12}")
        print("-"*70)
        
        for item in low_stock_items:
            severity_display = "🔴 CRITICAL" if item['severity'] == "CRITICAL" else "🟡 LOW"
            print(f"{severity_display:<12} {item['id']:<15} {item['name']:<25} {item['stock']:<12}")
        
        print("-"*70)
        print(f"Threshold: {self.threshold} units")
        print(f"Total low stock items: {len(low_stock_items)}")
        print("\n💡 Recommendation: Restock these items as soon as possible!")
    
    def set_threshold(self, new_threshold):
        """Update the low stock threshold"""
        if new_threshold >= 0:
            self.threshold = new_threshold
            print(f"✓ Low stock threshold updated to {new_threshold} units")
            return True
        else:
            print("❌ Threshold cannot be negative")
            return False