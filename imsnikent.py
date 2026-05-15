# inventory = {
#     "Laptop": {"price": 50000, "stock": 5},
#     "Mouse": {"price": 500, "stock": 20},
#     "Keyboard": {"price": 1500, "stock": 10}
# } for test

def calc_total_inventory():
    total = 0

    if not inventory:
        print("Walay man laman bai")

    for product, details in inventory.items(): # subject to change

        value = details["price"] * details["stock"]
        total += value

    print(f"Total Inventory Value: P{total}")

def view_sales_history():
    print("\nSales History")
    print("-" * 30)

    if not sales:
        print("aray mo walang nabenta")
        return

    for sale in sales_history: # subject to change
        print(
            f"Date: {sale['date']} | "
            f"Product: {sale['product']} | "
            f"Quantity: {sale['quantity']}"
        )
    
calc_total_inventory()
view_sales_history()