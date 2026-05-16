import json
import os

class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.price = float(price)
        self.stock = int(stock)

    def update_info(self, new_name=None, new_price=None):
        if new_name:
            self.name = new_name
        if new_price is not None:
            if new_price < 0:
                print("❌ Validation Error: Price cannot be negative.")
                return False
            self.price = float(new_price)
        print(f"✅ Product {self.product_id} information updated.")
        return True

    def update_stock(self, amount):
        # Amount can be positive (restocking) or negative (selling/removing)
        if self.stock + amount < 0:
            print(f"❌ Validation Error: Insufficient stock. Current stock is {self.stock}.")
            return False
        
        self.stock += amount
        action = "Added" if amount > 0 else "Removed"
        print(f"✅ {action} {abs(amount)} units. New stock level for '{self.name}': {self.stock}")
        return True

    def to_dict(self):
        """Serializes the object for JSON storage."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock
        }

class InventoryManager:
    def __init__(self, filename="inventory_database.json"):
        self.filename = filename
        self.products = {}
        self.load_data()  # C++ Equivalent: std::ifstream

    def load_data(self):
        """Reads from the file stream on startup to restore previous inventory."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as file:
                try:
                    data = json.load(file)
                    for p_id, p_data in data.items():
                        self.products[p_id] = Product(p_id, p_data["name"], p_data["price"], p_data["stock"])
                    print(f"📁 Loaded {len(self.products)} products from database.")
                except json.JSONDecodeError:
                    print("⚠️ Database file corrupted or empty. Starting fresh.")
        else:
            print("🆕 No existing database found. Starting fresh.")

    def save_data(self):
        """Writes to the file stream to persist current inventory state."""
        # C++ Equivalent: std::ofstream
        with open(self.filename, 'w') as file:
            data = {p_id: p.to_dict() for p_id, p in self.products.items()}
            json.dump(data, file, indent=4)

    def add_product(self, product_id, name, price, initial_stock):
        if product_id in self.products:
            print(f"\n⚠️ Product ID '{product_id}' already exists!")
            return
        
        if price < 0 or initial_stock < 0:
            print("\n❌ Validation Error: Price and stock cannot be negative.")
            return

        self.products[product_id] = Product(product_id, name, price, initial_stock)
        print(f"\n🌟 Product '{name}' (ID: {product_id}) added successfully.")
        self.save_data()

    def modify_product_info(self, product_id, new_name=None, new_price=None):
        if product_id not in self.products:
            print("\n⚠️ Product not found!")
            return
        
        success = self.products[product_id].update_info(new_name, new_price)
        if success:
            self.save_data()

    def adjust_stock(self, product_id, amount):
        if product_id not in self.products:
            print("\n⚠️ Product not found!")
            return
        
        success = self.products[product_id].update_stock(amount)
        if success:
            self.save_data()

    def display_inventory(self):
        if not self.products:
            print("\n📭 Inventory is empty.")
            return
        print("\n=== Current Inventory ===")
        print(f"{'ID':<10} | {'Product Name':<20} | {'Price':<10} | {'Stock':<10}")
        print("-" * 58)
        for p_id, p in self.products.items():
            print(f"{p_id:<10} | {p.name:<20} | ${p.price:<9.2f} | {p.stock:<10}")


# --- Interactive User Interface Loop ---
def main():
    inventory = InventoryManager()
    
    while True:
        print("\n==============================")
        print("  INVENTORY PERSISTENCE CLI   ")
        print("==============================")
        print("1. Add New Product")
        print("2. Update Product Info")
        print("3. Adjust Stock Levels")
        print("4. View Inventory")
        print("5. Exit Application")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            p_id = input("Enter Product ID: ").strip()
            if not p_id:
                print("⚠️ ID cannot be empty.")
                continue
            name = input("Enter Product Name: ").strip()
            try:
                price = float(input("Enter Price: $"))
                stock = int(input("Enter Initial Stock: "))
                inventory.add_product(p_id, name, price, stock)
            except ValueError:
                print("❌ Invalid input! Price must be a number, stock must be an integer.")
                
        elif choice == '2':
            p_id = input("Enter Product ID to update: ").strip()
            print("Leave fields blank and press Enter if you do not want to change them.")
            new_name = input("Enter new name: ").strip()
            price_input = input("Enter new price: $").strip()
            
            new_price = None
            if price_input:
                try:
                    new_price = float(price_input)
                except ValueError:
                    print("❌ Invalid price format. Update aborted.")
                    continue
            
            # Pass None if the user left the name blank
            inventory.modify_product_info(p_id, new_name if new_name else None, new_price)
                
        elif choice == '3':
            p_id = input("Enter Product ID: ").strip()
            try:
                print("Tip: Use positive numbers to restock, negative numbers to reduce stock.")
                amount = int(input("Enter stock adjustment amount: "))
                inventory.adjust_stock(p_id, amount)
            except ValueError:
                print("❌ Invalid input! Stock amount must be an integer.")
                
        elif choice == '4':
            inventory.display_inventory()
            
        elif choice == '5':
            print("\n💾 Data automatically synced. Goodbye!")
            break
        else:
            print("\n⚠️ Invalid option. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()