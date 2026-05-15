def calc_total_inventory():
    total = 0

    for product, details in inventory.items(): # subject to change
        value = details["price"] * details["stock"]
        total += value

    print(f"Total Inventory Value: P{total}")

def view_sales_history():
    print("\nSales History")
    print("-" * 30)

    for sale in sales_history: # subject to change
        print(
            f"Date: {sale['date']} | "
            f"Product: {sale['product']} | "
            f"Quantity: {sale['quantity']}"
        )
    
calc_total_inventory()
view_sales_history()