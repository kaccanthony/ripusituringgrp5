import datetime

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────

LOW_STOCK_THRESHOLD = 5

SEPARATOR = "=" * 65
THIN_SEP  = "-" * 65

KEYWORDS = {
    "clothing":    ["shirt", "pant", "jean", "shoe", "sock", "hat", "jacket"],
    "electronics": ["phone", "laptop", "camera", "tablet", "headphone", "charger"],
    "food":        ["apple", "bread", "milk", "cheese", "chocolate", "snack", "burger"],
    "home":        ["sofa", "chair", "table", "lamp", "bed", "pillow"],
    "beauty":      ["soap", "shampoo", "cream", "perfume", "lotion"],
    "toy":         ["toy", "game", "puzzle", "lego", "doll"],
}


# ─────────────────────────────────────────────
#  PRODUCT CLASS
# ─────────────────────────────────────────────

class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name       = name
        self.price      = float(price)
        self.stock      = int(stock)
        self.category   = classify(name)   # auto-classify on creation

    def update_info(self, new_name=None, new_price=None):
        if new_name:
            self.name     = new_name
            self.category = classify(new_name)   # re-classify if name changes
        if new_price is not None:
            if new_price < 0:
                print("   Price cannot be negative.")
                return False
            self.price = float(new_price)
        print(f"   Product {self.product_id} information updated.")
        return True

    def update_stock(self, amount):
        if self.stock + amount < 0:
            print(f"   Insufficient stock. Current stock is {self.stock}.")
            return False
        self.stock += amount
        action = "Added" if amount > 0 else "Removed"
        print(f"   {action} {abs(amount)} unit(s). '{self.name}' stock: {self.stock}")
        return True

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "name":       self.name,
            "price":      self.price,
            "stock":      self.stock,
            "category":   self.category,
        }


# ─────────────────────────────────────────────
#  PRODUCT CLASSIFICATION
# ─────────────────────────────────────────────

def classify(name):
    """Keyword-based category classifier."""
    n = str(name).strip().lower()
    if not n:
        return "unknown"
    for cat, keys in KEYWORDS.items():
        if any(k in n for k in keys):
            return cat
    return "other"

def annotate(items):
    """Add category field to a list of plain dicts (used for search)."""
    return [{**item, "category": classify(item.get("name", ""))} for item in items]

def search(items, query):
    """Search a list of plain dicts by name or category keyword."""
    q = str(query).strip().lower()
    if not q:
        return []
    annotated = annotate(items)
    return [
        item for item in annotated
        if q in item["category"] or q in item.get("name", "").lower()
    ]

def classify_products(items):
    """Return (name, category) tuples for a list of plain dicts."""
    return [(item.get("name", ""), classify(item.get("name", ""))) for item in items]


# ─────────────────────────────────────────────
#  SALES TRANSACTION CLASSES
# ─────────────────────────────────────────────

class SalesTransaction:
    def __init__(self, transaction_id, product_id, product_name,
                quantity, price_per_unit, total_amount, date=None):
        self.transaction_id  = transaction_id
        self.product_id      = product_id
        self.product_name    = product_name
        self.quantity        = quantity
        self.price_per_unit  = price_per_unit
        self.total_amount    = total_amount
        self.date            = date if date else datetime.datetime.now()

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "product_id":     self.product_id,
            "product_name":   self.product_name,
            "quantity":       self.quantity,
            "price_per_unit": self.price_per_unit,
            "total_amount":   self.total_amount,
            "date":           self.date.isoformat(),
        }

    def display(self):
        print(f"  ID: {self.transaction_id} | Product: {self.product_name} | "
              f"Qty: {self.quantity} | Total: ${self.total_amount:.2f} | "
              f"Date: {self.date.strftime('%Y-%m-%d %H:%M')}")


class SalesManager:
    def __init__(self):
        self.transactions = []
        self.next_id      = 1

    def record_sale(self, product_id, product_name, quantity, price_per_unit, current_stock):
        """
        Record a sale. Returns (success, message, transaction_object).
        Does NOT modify stock — InventoryManager handles that.
        """
        if quantity <= 0:
            return False, "Quantity must be greater than zero.", None
        if current_stock < quantity:
            return False, f"Insufficient stock! Only {current_stock} unit(s) available.", None

        total_amount = quantity * price_per_unit
        transaction  = SalesTransaction(
            self.next_id, product_id, product_name,
            quantity, price_per_unit, total_amount
        )
        self.transactions.append(transaction)
        self.next_id += 1
        return True, f"Sale recorded! Total: ${total_amount:.2f}", transaction

    def get_sales_history(self, limit=None):
        sorted_tx = sorted(self.transactions, key=lambda x: x.date, reverse=True)
        return sorted_tx[:limit] if limit else sorted_tx

    def get_total_revenue(self):
        return sum(t.total_amount for t in self.transactions)

    def display_sales_history(self, limit=20):
        if not self.transactions:
            print("\n   No sales transactions found.")
            return
        history = self.get_sales_history(limit)
        print(f"\n  {'ID':<6} {'Product':<22} {'Qty':<6} {'Unit Price':<13} {'Total':<13} {'Date'}")
        print("  " + THIN_SEP)
        for t in history:
            print(f"  {t.transaction_id:<6} {t.product_name:<22} {t.quantity:<6} "
                  f"${t.price_per_unit:<12.2f} ${t.total_amount:<12.2f} "
                  f"{t.date.strftime('%Y-%m-%d %H:%M')}")
        print("  " + THIN_SEP)
        print(f"  Total Revenue : ${self.get_total_revenue():,.2f}")
        if len(self.transactions) > limit:
            print(f"  (Showing last {limit} of {len(self.transactions)} transactions)")


# ─────────────────────────────────────────────
#  LOW STOCK ALERT SYSTEM
# ─────────────────────────────────────────────

class LowStockAlert:
    def __init__(self, threshold=LOW_STOCK_THRESHOLD):
        self.threshold = threshold

    def check_product_stock(self, product_id, product_name, current_stock):
        """Returns (is_low, alert_message, severity)."""
        if current_stock <= 0:
            return True, f"CRITICAL: '{product_name}' (ID: {product_id}) is OUT OF STOCK!", "CRITICAL"
        elif current_stock <= self.threshold:
            return True, (f"LOW STOCK: '{product_name}' (ID: {product_id}) "
                          f"has {current_stock} unit(s) left (threshold: {self.threshold})"), "LOW"
        return False, "", "OK"

    def get_low_stock_products(self, products_dict):
        """Returns a list of dicts for all products at or below threshold."""
        results = []
        for pid, product in products_dict.items():
            is_low, _, severity = self.check_product_stock(pid, product.name, product.stock)
            if is_low:
                results.append({
                    "id":       pid,
                    "name":     product.name,
                    "stock":    product.stock,
                    "severity": severity,
                })
        return results

    def display_alerts(self, products_dict):
        low_items = self.get_low_stock_products(products_dict)
        if not low_items:
            print(f"\n   All products have sufficient stock (threshold: {self.threshold} units).")
            return
        print(f"\n  {'Severity':<14} {'Product ID':<14} {'Product Name':<25} {'Stock':>5}")
        print("  " + THIN_SEP)
        for item in low_items:
            sev = " CRITICAL" if item["severity"] == "CRITICAL" else "LOW     "
            print(f"  {sev:<14} {item['id']:<14} {item['name']:<25} {item['stock']:>5}")
        print("  " + THIN_SEP)
        print(f"  Threshold: {self.threshold} units | Items flagged: {len(low_items)}")
        print("   Restock these items as soon as possible!")

    def set_threshold(self, new_threshold):
        if new_threshold >= 0:
            self.threshold = new_threshold
            print(f"   Low stock threshold updated to {new_threshold} units.")
            return True
        print("   Threshold cannot be negative.")
        return False


# ─────────────────────────────────────────────
#  INVENTORY MANAGER  (in-memory, no file I/O)
# ─────────────────────────────────────────────

class InventoryManager:
    def __init__(self):
        self.products     = {}
        self.sales_mgr    = SalesManager()
        self.alert_system = LowStockAlert()
        self._load_test_products()

    def _load_test_products(self):
        """Predefined products for testing."""
        test_data = [
            ("P001", "Laptop",        45999.00, 10),
            ("P002", "Wireless Mouse",  899.00, 3),   # will trigger LOW alert
            ("P003", "Mechanical Keyboard", 1499.00, 0),  # will trigger CRITICAL
            ("P004", "USB-C Charger",   599.00, 15),
            ("P005", "Red Shirt",       399.00, 8),
            ("P006", "Blue Jeans",      799.00, 5),   # will trigger LOW alert
            ("P007", "Chocolate Bar",    49.00, 50),
            ("P008", "Desk Lamp",       999.00, 2),   # will trigger LOW alert
        ]
        for pid, name, price, stock in test_data:
            self.products[pid] = Product(pid, name, price, stock)
        print(f"   {len(self.products)} test products loaded.")

    # ── Product lookup ───────────────────────

    def product_exists(self, product_id):
        return product_id in self.products

    def get_product(self, product_id):
        p = self.products.get(product_id)
        if not p:
            print(f"   Product ID '{product_id}' not found in the system.")
        return p

    # ── Core CRUD ────────────────────────────

    def add_product(self, product_id, name, price, initial_stock):
        if product_id in self.products:
            print(f"    Product ID '{product_id}' already exists!")
            return
        if price < 0 or initial_stock < 0:
            print("   Price and stock cannot be negative.")
            return
        self.products[product_id] = Product(product_id, name, price, initial_stock)
        cat = self.products[product_id].category
        print(f"   '{name}' (ID: {product_id}, Category: {cat}) added successfully.")

    def modify_product_info(self, product_id, new_name=None, new_price=None):
        p = self.get_product(product_id)
        if p:
            p.update_info(new_name, new_price)

    def adjust_stock(self, product_id, amount):
        p = self.get_product(product_id)
        if p:
            p.update_stock(amount)

    def display_inventory(self):
        if not self.products:
            print("\n   Inventory is empty.")
            return
        print(f"\n  {'ID':<10} | {'Product Name':<22} | {'Category':<12} | {'Price':>10} | {'Stock':>6}")
        print("  " + THIN_SEP)
        for pid, p in self.products.items():
            print(f"  {pid:<10} | {p.name:<22} | {p.category:<12} | ${p.price:>9,.2f} | {p.stock:>6}")

    # ── Sales ────────────────────────────────

    def process_sale(self, product_id, quantity):
        p = self.get_product(product_id)
        if not p:
            return
        success, msg, tx = self.sales_mgr.record_sale(
            product_id, p.name, quantity, p.price, p.stock
        )
        if success:
            p.update_stock(-quantity)    # deduct stock after sale confirmed
            print(f"   {msg}")
            # auto-check alert after sale
            is_low, alert_msg, _ = self.alert_system.check_product_stock(product_id, p.name, p.stock)
            if is_low:
                print(f"\n    {alert_msg}")
        else:
            print(f"   {msg}")

    # ── Analytics ────────────────────────────

    def calc_total_inventory_value(self):
        """Calculate total value of all stock on hand (price × stock for each product)."""
        if not self.products:
            print("   Inventory is empty.")
            return
        total = sum(p.price * p.stock for p in self.products.values())
        print(f"\n  {'Product':<22} {'Category':<12} {'Price':>10}   {'Stock':>6}   {'Value':>12}")
        print("  " + THIN_SEP)
        for p in self.products.values():
            value = p.price * p.stock
            print(f"  {p.name:<22} {p.category:<12} ${p.price:>9,.2f}   {p.stock:>6}   ${value:>11,.2f}")
        print("  " + THIN_SEP)
        print(f"  {'Total Inventory Value:':<42} ${total:>11,.2f}")

    # ── Search ───────────────────────────────

    def search_products(self, query):
        """Search by product name or category keyword."""
        items = [{"id": pid, "name": p.name, "price": str(p.price), "stock": p.stock}
                 for pid, p in self.products.items()]
        results = search(items, query)
        if not results:
            print(f"\n  No products found matching '{query}'.")
            print("  Try a product name or category (clothing, electronics, food, home, beauty, toy).")
            return
        print(f"\n  {'ID':<10} | {'Category':<12} | {'Name':<22} | {'Price':>10} | {'Stock':>6}")
        print("  " + THIN_SEP)
        for r in results:
            pid   = r["id"]
            p     = self.products[pid]
            print(f"  {pid:<10} | {r['category']:<12} | {p.name:<22} | ${p.price:>9,.2f} | {p.stock:>6}")


# ─────────────────────────────────────────────
#  INPUT HELPERS
# ─────────────────────────────────────────────

def section_header(title):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)

def prompt_valid_product(inventory, label="product ID"):
    """
    Loops until a valid existing product ID is entered, or -1 to cancel.
    Error prints immediately before re-prompting.
    """
    while True:
        raw = input(f"\n  Enter {label} (-1 to cancel): ").strip()
        if raw == "-1":
            print("  ↩  Cancelled.")
            return None
        if not raw:
            print("    Product ID cannot be empty. Try again.")
            continue
        if inventory.product_exists(raw):
            return raw
        print(f"   Product ID '{raw}' not found in the system. Try again.")

def prompt_int(label):
    while True:
        raw = input(f"  {label} (-1 to cancel): ").strip()
        if raw == "-1":
            print("  ↩  Cancelled.")
            return None
        try:
            return int(raw)
        except ValueError:
            print("   Please enter a whole number.")

def prompt_float(label):
    while True:
        raw = input(f"  {label} (-1 to cancel): $").strip()
        if raw == "-1":
            print("  ↩  Cancelled.")
            return None
        try:
            return float(raw)
        except ValueError:
            print("   Please enter a valid number.")


# ─────────────────────────────────────────────
#  MENU ACTIONS
# ─────────────────────────────────────────────

def menu_add_product(inv):
    section_header("ADD NEW PRODUCT")
    while True:
        pid = input("  Enter Product ID (-1 to cancel): ").strip()
        if pid == "-1":
            print("  ↩  Cancelled.")
            return
        if not pid:
            print("    ID cannot be empty.")
            continue
        if inv.product_exists(pid):
            print(f"    Product ID '{pid}' already exists. Try a different ID.")
            continue
        break

    name = input("  Enter Product Name: ").strip()
    if not name:
        print("    Name cannot be empty. Aborted.")
        return

    price = prompt_float("Enter Price")
    if price is None:
        return
    stock = prompt_int("Enter Initial Stock")
    if stock is None:
        return

    inv.add_product(pid, name, price, stock)


def menu_update_product(inv):
    section_header("UPDATE PRODUCT INFO")
    pid = prompt_valid_product(inv)
    if pid is None:
        return

    p = inv.products[pid]
    print(f"\n  Current — Name: {p.name} | Price: ${p.price:,.2f}")
    print("  (Leave blank and press Enter to keep current value)")

    new_name  = input("  New name: ").strip()
    price_raw = input("  New price: $").strip()

    new_price = None
    if price_raw:
        try:
            new_price = float(price_raw)
        except ValueError:
            print("   Invalid price. Update aborted.")
            return

    inv.modify_product_info(pid, new_name if new_name else None, new_price)


def menu_adjust_stock(inv):
    section_header("ADJUST STOCK LEVELS")
    pid = prompt_valid_product(inv)
    if pid is None:
        return
    print("  Tip: Use positive to restock, negative to reduce.")
    amount = prompt_int("Enter stock adjustment")
    if amount is not None:
        inv.adjust_stock(pid, amount)


def menu_view_inventory(inv):
    section_header("CURRENT INVENTORY")
    inv.display_inventory()


def menu_process_sale(inv):
    section_header("PROCESS SALE")
    pid = prompt_valid_product(inv)
    if pid is None:
        return
    p = inv.products[pid]
    print(f"  Product: {p.name} | Price: ${p.price:,.2f} | Stock: {p.stock}")
    qty = prompt_int("Enter quantity to sell")
    if qty is not None:
        inv.process_sale(pid, qty)


def menu_sales_history(inv):
    section_header("SALES HISTORY")
    inv.sales_mgr.display_sales_history()


def menu_low_stock_alerts(inv):
    section_header("LOW STOCK ALERTS")
    inv.alert_system.display_alerts(inv.products)
    print(f"\n  Current threshold: {inv.alert_system.threshold} units")
    change = input("  Change threshold? (y/n): ").strip().lower()
    if change == "y":
        new_t = prompt_int("Enter new threshold")
        if new_t is not None:
            inv.alert_system.set_threshold(new_t)


def menu_total_inventory_value(inv):
    section_header("TOTAL INVENTORY VALUE")
    inv.calc_total_inventory_value()


def menu_search_products(inv):
    section_header("SEARCH PRODUCTS")
    print("  Categories: clothing, electronics, food, home, beauty, toy, other")
    query = input("  Enter product name or category to search: ").strip()
    if query:
        inv.search_products(query)
    else:
        print("    Search query cannot be empty.")


# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────

MENU_OPTIONS = [
    ("1",  "Add New Product",          menu_add_product),
    ("2",  "Update Product Info",      menu_update_product),
    ("3",  "Adjust Stock Levels",      menu_adjust_stock),
    ("4",  "Process Sale",             menu_process_sale),
    ("5",  "View Inventory",           menu_view_inventory),
    ("6",  "Sales History",            menu_sales_history),
    ("7",  "Low Stock Alerts",         menu_low_stock_alerts),
    ("8",  "Total Inventory Value",    menu_total_inventory_value),
    ("9",  "Search Products",          menu_search_products),
    ("10", "Exit",                     None),
]

def print_main_menu():
    print(f"\n{SEPARATOR}")
    print("       INVENTORY MANAGEMENT SYSTEM")
    print(SEPARATOR)
    for key, label, _ in MENU_OPTIONS:
        print(f"  {key:>2}. {label}")
    print(SEPARATOR)

def main():
    print(f"\n{SEPARATOR}")
    print("  Initializing Inventory System...")
    print(SEPARATOR)
    inv = InventoryManager()

    while True:
        print_main_menu()
        choice = input("\n  Enter your choice: ").strip()

        if choice == "10":
            print("\n   Goodbye!\n")
            break

        matched = next((fn for key, _, fn in MENU_OPTIONS if key == choice and fn), None)
        if matched:
            matched(inv)
        elif choice not in {key for key, _, _ in MENU_OPTIONS}:
            print(f"\n    Invalid option. Please enter 1–{len(MENU_OPTIONS)}.")


if __name__ == "__main__":
    main()