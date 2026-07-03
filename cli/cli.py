"""
CLI Interface for Inventory Management System
Interactive command-line tool for managing inventory
"""

import click
import requests
import json
from typing import Optional
from tabulate import tabulate

# API base URL
API_BASE_URL = "http://localhost:5000/api"


class InventoryClient:
    """Client for interacting with the Inventory API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response.json(), response.status_code
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Cannot connect to API. Is the server running?"
            }, 500
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    
    # ============== PRODUCT OPERATIONS ==============
    
    def list_products(self):
        """Get all products"""
        return self._make_request("GET", "/products")
    
    def get_product(self, product_id: int):
        """Get product by ID"""
        return self._make_request("GET", f"/products/{product_id}")
    
    def create_product(self, product_data: dict):
        """Create new product"""
        return self._make_request(
            "POST",
            "/products",
            json=product_data
        )
    
    def update_product(self, product_id: int, product_data: dict):
        """Update product"""
        return self._make_request(
            "PATCH",
            f"/products/{product_id}",
            json=product_data
        )
    
    def delete_product(self, product_id: int):
        """Delete product"""
        return self._make_request("DELETE", f"/products/{product_id}")
    
    def search_by_name(self, query: str):
        """Search products by name"""
        return self._make_request(
            "GET",
            "/products/search/name",
            params={"query": query}
        )
    
    def search_by_barcode(self, barcode: str):
        """Search products by barcode"""
        return self._make_request(
            "GET",
            "/products/search/barcode",
            params={"barcode": barcode}
        )
    
    # ============== EXTERNAL API OPERATIONS ==============
    
    def search_external_api(self, query: str, limit: int = 10):
        """Search OpenFoodFacts API"""
        return self._make_request(
            "GET",
            "/external/search",
            params={"query": query, "limit": limit}
        )
    
    def fetch_by_barcode_external(self, barcode: str):
        """Fetch product from OpenFoodFacts by barcode"""
        return self._make_request(
            "GET",
            f"/external/barcode/{barcode}"
        )
    
    def add_from_external_api(self, barcode: str, price: float, quantity: int = 0):
        """Add product from OpenFoodFacts to inventory"""
        return self._make_request(
            "POST",
            "/products/external-add",
            json={
                "barcode": barcode,
                "price": price,
                "quantity": quantity
            }
        )


# Initialize CLI client
client = InventoryClient()


# ============== CLI COMMANDS ==============

@click.group()
def cli():
    """Inventory Management System - CLI Tool"""
    pass


# ---------- List Commands ----------

@cli.command()
def list_all():
    """Display all inventory items"""
    try:
        data, status_code = client.list_products()
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        products = data.get("data", [])
        
        if not products:
            click.secho("No products in inventory", fg='yellow')
            return
        
        # Format for tabulate
        headers = ["ID", "Product Name", "Brand", "Quantity", "Price", "Category"]
        rows = [
            [
                p["id"],
                p.get("product_name", "N/A")[:30],
                p.get("brands", "N/A")[:20],
                p.get("quantity", 0),
                f"${p.get('price', 0):.2f}",
                p.get("category", "N/A")
            ]
            for p in products
        ]
        
        click.echo("\n" + tabulate(rows, headers=headers, tablefmt="grid") + "\n")
        click.secho(f"Total: {len(products)} products", fg='green')
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


@cli.command()
@click.option('--id', type=int, required=True, help='Product ID')
def view(id):
    """View details of a specific product"""
    try:
        data, status_code = client.get_product(id)
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        product = data.get("data", {})
        
        click.echo("\n" + "="*60)
        click.secho(f"Product ID: {product['id']}", fg='cyan', bold=True)
        click.echo("="*60)
        click.echo(f"Name:            {product.get('product_name', 'N/A')}")
        click.echo(f"Brand:           {product.get('brands', 'N/A')}")
        click.echo(f"Barcode:         {product.get('barcode', 'N/A')}")
        click.echo(f"Category:        {product.get('category', 'N/A')}")
        click.echo(f"Quantity:        {product.get('quantity', 0)} units")
        click.echo(f"Price:           ${product.get('price', 0):.2f}")
        click.echo(f"\nIngredients:     {product.get('ingredients_text', 'N/A')}")
        
        nutrition = product.get("nutrition_facts", {})
        if nutrition:
            click.echo("\nNutrition Facts (per 100g):")
            click.echo(f"  Calories:      {nutrition.get('calories', 0)} kcal")
            click.echo(f"  Fat:           {nutrition.get('fat', 0)}g")
            click.echo(f"  Protein:       {nutrition.get('protein', 0)}g")
            click.echo(f"  Carbs:         {nutrition.get('carbohydrates', 0)}g")
        
        click.echo("="*60 + "\n")
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- Add Commands ----------

@cli.command()
def add():
    """Add a new inventory item"""
    try:
        click.secho("\n--- Add New Product ---", fg='cyan', bold=True)
        
        name = click.prompt("Product name")
        brand = click.prompt("Brand", default="")
        barcode = click.prompt("Barcode", default="")
        category = click.prompt("Category", default="Other")
        quantity = click.prompt("Quantity", type=int, default=0)
        price = click.prompt("Price ($)", type=float)
        ingredients = click.prompt("Ingredients (optional)", default="")
        
        product_data = {
            "product_name": name,
            "brands": brand,
            "barcode": barcode,
            "category": category,
            "quantity": quantity,
            "price": price,
            "ingredients_text": ingredients
        }
        
        data, status_code = client.create_product(product_data)
        
        if status_code == 201:
            product = data.get("data", {})
            click.secho(
                f"✓ Product added successfully (ID: {product['id']})",
                fg='green'
            )
        else:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
        
    except click.Abort:
        click.secho("Cancelled", fg='yellow')
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- Update Commands ----------

@cli.command()
@click.option('--id', type=int, required=True, help='Product ID')
@click.option('--quantity', type=int, help='New quantity')
@click.option('--price', type=float, help='New price')
def update(id, quantity, price):
    """Update product quantity or price"""
    try:
        update_data = {}
        
        if quantity is not None:
            update_data["quantity"] = quantity
        if price is not None:
            update_data["price"] = price
        
        if not update_data:
            click.secho("No fields to update", fg='yellow')
            return
        
        data, status_code = client.update_product(id, update_data)
        
        if status_code == 200:
            click.secho("✓ Product updated successfully", fg='green')
        else:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- Delete Commands ----------

@cli.command()
@click.option('--id', type=int, required=True, help='Product ID')
@click.confirmation_option(prompt='Are you sure you want to delete this product?')
def delete(id):
    """Delete a product from inventory"""
    try:
        data, status_code = client.delete_product(id)
        
        if status_code == 200:
            click.secho("✓ Product deleted successfully", fg='green')
        else:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- Search Commands ----------

@cli.command()
@click.argument('query')
def search(query):
    """Search products by name"""
    try:
        data, status_code = client.search_by_name(query)
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        products = data.get("data", [])
        
        if not products:
            click.secho(f"No products found matching '{query}'", fg='yellow')
            return
        
        headers = ["ID", "Product Name", "Brand", "Quantity", "Price"]
        rows = [
            [
                p["id"],
                p.get("product_name", "N/A")[:30],
                p.get("brands", "N/A")[:20],
                p.get("quantity", 0),
                f"${p.get('price', 0):.2f}"
            ]
            for p in products
        ]
        
        click.echo("\n" + tabulate(rows, headers=headers, tablefmt="grid") + "\n")
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


@cli.command()
@click.argument('barcode')
def search_barcode(barcode):
    """Search product by barcode"""
    try:
        data, status_code = client.search_by_barcode(barcode)
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        product = data.get("data", {})
        click.secho(f"\n✓ Found: {product.get('product_name')} by {product.get('brands')}", fg='green')
        click.echo(f"  Quantity: {product.get('quantity')} | Price: ${product.get('price'):.2f}")
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- External API Commands ----------

@cli.command()
@click.argument('query')
@click.option('--limit', type=int, default=10, help='Max results')
def search_api(query, limit):
    """Search OpenFoodFacts API for products"""
    try:
        click.secho(f"Searching OpenFoodFacts for '{query}'...", fg='cyan')
        data, status_code = client.search_external_api(query, limit)
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        products = data.get("data", [])
        
        if not products:
            click.secho("No products found", fg='yellow')
            return
        
        headers = ["#", "Product Name", "Brand", "Category"]
        rows = [
            [
                i+1,
                p.get("product_name", "N/A")[:40],
                p.get("brands", "N/A")[:20],
                p.get("category", "N/A")[:20]
            ]
            for i, p in enumerate(products)
        ]
        
        click.echo("\n" + tabulate(rows, headers=headers, tablefmt="grid") + "\n")
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


@cli.command()
@click.argument('barcode')
def search_api_barcode(barcode):
    """Fetch product from OpenFoodFacts by barcode"""
    try:
        click.secho(f"Fetching product {barcode} from OpenFoodFacts...", fg='cyan')
        data, status_code = client.fetch_by_barcode_external(barcode)
        
        if status_code != 200:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
            return
        
        product = data.get("data", {})
        
        click.secho(f"\n✓ Found: {product.get('product_name')}", fg='green')
        click.echo(f"  Brand: {product.get('brands', 'N/A')}")
        click.echo(f"  Category: {product.get('category', 'N/A')}")
        click.echo(f"  Ingredients: {product.get('ingredients_text', 'N/A')[:100]}...")
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


@cli.command()
@click.argument('barcode')
@click.option('--price', type=float, required=True, help='Price to set')
@click.option('--quantity', type=int, default=0, help='Initial quantity')
def add_from_api(barcode, price, quantity):
    """Add product from OpenFoodFacts to inventory"""
    try:
        click.secho(
            f"Adding product {barcode} from OpenFoodFacts...",
            fg='cyan'
        )
        
        data, status_code = client.add_from_external_api(barcode, price, quantity)
        
        if status_code == 201:
            product = data.get("data", {})
            click.secho(
                f"✓ Added to inventory (ID: {product['id']})",
                fg='green'
            )
            click.echo(f"  Product: {product.get('product_name')}")
            click.echo(f"  Price: ${product.get('price'):.2f}")
            click.echo(f"  Quantity: {product.get('quantity')}")
        else:
            click.secho(f"Error: {data.get('message', 'Unknown error')}", fg='red')
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')


# ---------- Help Command ----------

@cli.command()
def help_commands():
    """Show all available commands"""
    click.echo("""
╔════════════════════════════════════════════════════════════════╗
║     INVENTORY MANAGEMENT SYSTEM - CLI COMMANDS                ║
╚════════════════════════════════════════════════════════════════╝

📋 VIEW COMMANDS:
  list-all              - Display all inventory items
  view --id ID          - View specific product details
  search QUERY          - Search products by name
  search-barcode CODE   - Search product by barcode

➕ ADD COMMANDS:
  add                   - Add new inventory item manually
  add-from-api CODE     - Add product from OpenFoodFacts by barcode

✏️  UPDATE COMMANDS:
  update --id ID [options]  - Update product
    --quantity N          Update stock quantity
    --price P             Update price

🗑️  DELETE COMMANDS:
  delete --id ID        - Delete product from inventory

🔍 EXTERNAL API COMMANDS:
  search-api QUERY      - Search OpenFoodFacts API
    --limit N            Max results (default 10)
  search-api-barcode CODE - Find product on OpenFoodFacts

ℹ️  OTHER:
  help-commands         - Show this help message

╔════════════════════════════════════════════════════════════════╗
Example Usage:
  inv list-all
  inv view --id 1
  inv search "milk"
  inv update --id 1 --quantity 50 --price 4.99
  inv delete --id 2
  inv search-api "almond milk"
  inv add-from-api 025005378348 --price 3.99 --quantity 10
╚════════════════════════════════════════════════════════════════╝
    """)


if __name__ == '__main__':
    cli()
