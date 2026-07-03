"""
Flask API Routes - REST endpoints for inventory management
Implements CRUD operations and external API integration
"""

from flask import Blueprint, request, jsonify
from app.database.mock_db import (
    get_all_products,
    get_product_by_id,
    get_product_by_name,
    get_product_by_barcode,
    add_product,
    update_product,
    delete_product
)
from app.services.openfoodfacts_service import get_service

api_blueprint = Blueprint('api', __name__, url_prefix='/api')


# ============== HEALTH CHECK ==============
@api_blueprint.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Inventory Management API is running"
    }), 200


# ============== INVENTORY CRUD OPERATIONS ==============

@api_blueprint.route('/products', methods=['GET'])
def get_products():
    """
    GET /api/products
    Retrieve all products from inventory
    
    Returns:
        List of all products with 200 status
    """
    try:
        products = get_all_products()
        return jsonify({
            "status": "success",
            "count": len(products),
            "data": products
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    GET /api/products/<id>
    Retrieve a specific product by ID
    """
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({
                "status": "error",
                "message": f"Product with ID {product_id} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": product
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products', methods=['POST'])
def create_product():
    """
    POST /api/products
    Create a new inventory item
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        if "product_name" not in data:
            return jsonify({
                "status": "error",
                "message": "product_name is required"
            }), 400
        
        if "price" not in data or "quantity" not in data:
            return jsonify({
                "status": "error",
                "message": "price and quantity are required"
            }), 400
        
        product = add_product(data)
        
        return jsonify({
            "status": "success",
            "message": "Product created successfully",
            "data": product
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products/<int:product_id>', methods=['PATCH'])
def update_product_endpoint(product_id):
    """
    PATCH /api/products/<id>
    Update an existing product
    """
    try:
        data = request.get_json(silent=True)
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        product = update_product(product_id, data)
        
        if not product:
            return jsonify({
                "status": "error",
                "message": f"Product with ID {product_id} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "message": "Product updated successfully",
            "data": product
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product_endpoint(product_id):
    """
    DELETE /api/products/<id>
    Delete a product from inventory
    """
    try:
        success = delete_product(product_id)
        
        if not success:
            return jsonify({
                "status": "error",
                "message": f"Product with ID {product_id} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "message": f"Product {product_id} deleted successfully"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============== SEARCH AND FILTER OPERATIONS ==============

@api_blueprint.route('/products/search/name', methods=['GET'])
def search_by_name():
    """
    GET /api/products/search/name?query=<name>
    Search products by name
    """
    try:
        query = request.args.get('query', '')
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "query parameter is required"
            }), 400
        
        products = get_product_by_name(query)
        
        return jsonify({
            "status": "success",
            "count": len(products),
            "data": products
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products/search/barcode', methods=['GET'])
def search_by_barcode():
    """
    GET /api/products/search/barcode?barcode=<code>
    Search products by barcode
    """
    try:
        barcode = request.args.get('barcode', '')
        
        if not barcode:
            return jsonify({
                "status": "error",
                "message": "barcode parameter is required"
            }), 400
        
        product = get_product_by_barcode(barcode)
        
        if not product:
            return jsonify({
                "status": "error",
                "message": f"Product with barcode {barcode} not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": product
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============== EXTERNAL API INTEGRATION ==============

@api_blueprint.route('/external/search', methods=['GET'])
def search_external_api():
    """
    GET /api/external/search?query=<query>
    Search OpenFoodFacts API for products
    """
    try:
        query = request.args.get('query', '')
        limit = request.args.get('limit', 10, type=int)
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "query parameter is required"
            }), 400
        
        if limit > 50:
            limit = 50
        
        service = get_service()
        products = service.search_products(query, limit)
        
        return jsonify({
            "status": "success",
            "count": len(products),
            "data": products,
            "source": "OpenFoodFacts API"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/external/barcode/<barcode>', methods=['GET'])
def fetch_by_barcode_external(barcode):
    """
    GET /api/external/barcode/<barcode>
    Fetch product data from OpenFoodFacts by barcode
    """
    try:
        if not barcode:
            return jsonify({
                "status": "error",
                "message": "barcode is required"
            }), 400
        
        service = get_service()
        product = service.get_product_by_barcode(barcode)
        
        if not product:
            return jsonify({
                "status": "error",
                "message": f"Product with barcode {barcode} not found in OpenFoodFacts"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": product,
            "source": "OpenFoodFacts API"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@api_blueprint.route('/products/external-add', methods=['POST'])
def add_from_external_api():
    """
    POST /api/products/external-add
    Fetch product from OpenFoodFacts and add to inventory
    """
    try:
        data = request.get_json(silent=True)
        
        if not data or "barcode" not in data:
            return jsonify({
                "status": "error",
                "message": "barcode is required"
            }), 400
        
        if "price" not in data:
            return jsonify({
                "status": "error",
                "message": "price is required"
            }), 400
        
        barcode = data.get("barcode")
        
        # Fetch from external API
        service = get_service()
        api_product = service.get_product_by_barcode(barcode)
        
        if not api_product:
            return jsonify({
                "status": "error",
                "message": f"Product with barcode {barcode} not found on OpenFoodFacts"
            }), 404
        
        # Add to inventory with user-provided price and quantity
        api_product["quantity"] = data.get("quantity", 0)
        api_product["price"] = data.get("price")
        
        product = add_product(api_product)
        
        return jsonify({
            "status": "success",
            "message": "Product added to inventory from OpenFoodFacts",
            "data": product
        }), 201
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============== ERROR HANDLERS ==============

@api_blueprint.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404


@api_blueprint.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "status": "error",
        "message": "Method not allowed"
    }), 405


@api_blueprint.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
