"""
Mock Database - Simulates OpenFoodFacts API structure
Stores product inventory with realistic product data
"""

# Mock database array with OpenFoodFacts-like structure
inventory_db = [
    {
        "id": 1,
        "product_name": "Organic Almond Milk",
        "brands": "Silk",
        "barcode": "025005378348",
        "quantity": 50,
        "price": 3.99,
        "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, potassium chloride, gum arabic, sunflower lecithin, vitamin E, vitamin A palmitate, vitamin D2",
        "nutrition_facts": {
            "calories": 30,
            "fat": 2.5,
            "protein": 1,
            "carbohydrates": 1
        },
        "category": "Beverages",
        "status": "active"
    },
    {
        "id": 2,
        "product_name": "Whole Wheat Bread",
        "brands": "Nature's Own",
        "barcode": "018000101010",
        "quantity": 25,
        "price": 2.49,
        "ingredients_text": "Whole wheat flour, water, yeast, salt, sugar, soybean oil, dough conditioner, ascorbic acid",
        "nutrition_facts": {
            "calories": 80,
            "fat": 1,
            "protein": 4,
            "carbohydrates": 14
        },
        "category": "Bakery",
        "status": "active"
    },
    {
        "id": 3,
        "product_name": "Greek Yogurt",
        "brands": "Fage",
        "barcode": "087680100087",
        "quantity": 40,
        "price": 4.99,
        "ingredients_text": "Milk, live active cultures (L. bulgaricus, S. thermophilus, L. acidophilus, Bifidus, L. casei)",
        "nutrition_facts": {
            "calories": 100,
            "fat": 5,
            "protein": 18,
            "carbohydrates": 7
        },
        "category": "Dairy",
        "status": "active"
    },
    {
        "id": 4,
        "product_name": "Organic Banana",
        "brands": "Fresh Farm",
        "barcode": "011110123456",
        "quantity": 100,
        "price": 0.59,
        "ingredients_text": "100% Organic Banana",
        "nutrition_facts": {
            "calories": 89,
            "fat": 0.3,
            "protein": 1.1,
            "carbohydrates": 23
        },
        "category": "Produce",
        "status": "active"
    },
    {
        "id": 5,
        "product_name": "Extra Virgin Olive Oil",
        "brands": "Kirkland",
        "barcode": "096619001015",
        "quantity": 15,
        "price": 12.99,
        "ingredients_text": "100% Extra Virgin Olive Oil",
        "nutrition_facts": {
            "calories": 120,
            "fat": 14,
            "protein": 0,
            "carbohydrates": 0
        },
        "category": "Oils & Condiments",
        "status": "active"
    }
]


def get_all_products():
    """Get all products from the database"""
    return inventory_db


def get_product_by_id(product_id):
    """Get a product by its ID"""
    for product in inventory_db:
        if product["id"] == product_id:
            return product
    return None


def get_product_by_name(name):
    """Get products by name (case-insensitive partial match)"""
    results = []
    for product in inventory_db:
        if name.lower() in product["product_name"].lower():
            results.append(product)
    return results


def get_product_by_barcode(barcode):
    """Get a product by barcode"""
    for product in inventory_db:
        if product["barcode"] == barcode:
            return product
    return None


def add_product(product_data):
    """Add a new product to the database"""
    # Generate new ID
    new_id = max([p["id"] for p in inventory_db]) + 1 if inventory_db else 1
    
    product = {
        "id": new_id,
        "product_name": product_data.get("product_name", "Unknown"),
        "brands": product_data.get("brands", ""),
        "barcode": product_data.get("barcode", ""),
        "quantity": product_data.get("quantity", 0),
        "price": product_data.get("price", 0.0),
        "ingredients_text": product_data.get("ingredients_text", ""),
        "nutrition_facts": product_data.get("nutrition_facts", {}),
        "category": product_data.get("category", "Other"),
        "status": "active"
    }
    
    inventory_db.append(product)
    return product


def update_product(product_id, product_data):
    """Update an existing product"""
    product = get_product_by_id(product_id)
    if not product:
        return None
    
    # Update fields
    product.update({
        "product_name": product_data.get("product_name", product["product_name"]),
        "brands": product_data.get("brands", product["brands"]),
        "barcode": product_data.get("barcode", product["barcode"]),
        "quantity": product_data.get("quantity", product["quantity"]),
        "price": product_data.get("price", product["price"]),
        "ingredients_text": product_data.get("ingredients_text", product["ingredients_text"]),
        "nutrition_facts": product_data.get("nutrition_facts", product["nutrition_facts"]),
        "category": product_data.get("category", product["category"])
    })
    
    return product


def delete_product(product_id):
    """Delete a product from the database"""
    global inventory_db
    product = get_product_by_id(product_id)
    if not product:
        return False
    
    inventory_db = [p for p in inventory_db if p["id"] != product_id]
    return True


def reset_database():
    """Reset database to initial state (for testing)"""
    global inventory_db
    inventory_db = [
        {
            "id": 1,
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "barcode": "025005378348",
            "quantity": 50,
            "price": 3.99,
            "ingredients_text": "Filtered water, almonds, cane sugar, sea salt, potassium chloride, gum arabic, sunflower lecithin, vitamin E, vitamin A palmitate, vitamin D2",
            "nutrition_facts": {
                "calories": 30,
                "fat": 2.5,
                "protein": 1,
                "carbohydrates": 1
            },
            "category": "Beverages",
            "status": "active"
        },
        {
            "id": 2,
            "product_name": "Whole Wheat Bread",
            "brands": "Nature's Own",
            "barcode": "018000101010",
            "quantity": 25,
            "price": 2.49,
            "ingredients_text": "Whole wheat flour, water, yeast, salt, sugar, soybean oil, dough conditioner, ascorbic acid",
            "nutrition_facts": {
                "calories": 80,
                "fat": 1,
                "protein": 4,
                "carbohydrates": 14
            },
            "category": "Bakery",
            "status": "active"
        },
        {
            "id": 3,
            "product_name": "Greek Yogurt",
            "brands": "Fage",
            "barcode": "087680100087",
            "quantity": 40,
            "price": 4.99,
            "ingredients_text": "Milk, live active cultures (L. bulgaricus, S. thermophilus, L. acidophilus, Bifidus, L. casei)",
            "nutrition_facts": {
                "calories": 100,
                "fat": 5,
                "protein": 18,
                "carbohydrates": 7
            },
            "category": "Dairy",
            "status": "active"
        },
        {
            "id": 4,
            "product_name": "Organic Banana",
            "brands": "Fresh Farm",
            "barcode": "011110123456",
            "quantity": 100,
            "price": 0.59,
            "ingredients_text": "100% Organic Banana",
            "nutrition_facts": {
                "calories": 89,
                "fat": 0.3,
                "protein": 1.1,
                "carbohydrates": 23
            },
            "category": "Produce",
            "status": "active"
        },
        {
            "id": 5,
            "product_name": "Extra Virgin Olive Oil",
            "brands": "Kirkland",
            "barcode": "096619001015",
            "quantity": 15,
            "price": 12.99,
            "ingredients_text": "100% Extra Virgin Olive Oil",
            "nutrition_facts": {
                "calories": 120,
                "fat": 14,
                "protein": 0,
                "carbohydrates": 0
            },
            "category": "Oils & Condiments",
            "status": "active"
        }
    ]
