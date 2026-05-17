from turtle import rt

KEYWORDS = {
    "clothing": ["shirt", "pant", "jean", "shoe", "sock", "hat", "jacket"],
    "electronics": ["phone", "laptop", "camera", "tablet", "headphone", "charger"],
    "food": ["apple", "bread", "milk", "cheese", "chocolate", "snack", "burger"],
    "home": ["sofa", "chair", "table", "lamp", "bed", "pillow"],
    "beauty": ["soap", "shampoo", "cream", "perfume", "lotion"],
    "toy": ["toy", "game", "puzzle", "lego", "doll"],
}

def classify(name):
    n = str(name).strip().lower()
    if not n:
        return "unknown"
    for cat, keys in KEYWORDS.items():
        if any(k in n for k in keys):
            return cat
    return "other"

def annotate(items):
    return [
        {**item, "category": classify(item.get("name", ""))}
        for item in items
    ]

def search(items, query):
    q = str(query).strip().lower()
    if not q:
        return []

    annotated = annotate(items)
    return [
        item
        for item in annotated
        if q in item["category"] or q in item.get("name", "").lower()
    ]

def classify_products(items):
    annotated = annotate(items)
    return [(item.get("name", ""), item["category"]) for item in annotated]

if __name__ == "__main__":
    items = [
        {"id": "1", "name": "Red Shirt", "price": "12.99"},
        {"id": "2", "name": "Blue Jeans", "price": "29.99"},
        {"id": "3", "name": "Green Hat", "price": "9.99"},
        {"id": "4", "name": "Yellow Socks", "price": "4.99"},
        {"id": "5", "name": "Smartphone", "price": "199.99"},
        {"id": "6", "name": "Chocolate Bar", "price": "1.99"},
        {"id": "7", "name": "Desk Lamp", "price": "24.99"},
        {"id": "8", "name": "Burger", "price": "5.99"},
    ]

    q = input("Search name or category: ")
    found = search(items, q)

    if found:
        for p in found:
            print(f"[{p['category']}] {p['name']} - ${p['price']}")
    else:
        print("No match.")
        print("Try checking your spelling or using a different category.")

    print("\nAll products:")
    for p in annotate(items):
        print(f"[{p['category']}] {p['name']} - ${p['price']}")
