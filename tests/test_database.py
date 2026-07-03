"""
Unit tests for Database functions
Tests mock database CRUD operations
"""

import pytest
from app.database.mock_db import (
    get_all_products,
    get_product_by_id,
    get_product_by_name,
    get_product_by_barcode,
    add_product,
    update_product,
    delete_product,
    reset_database,
)


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    reset_database()
    yield
    reset_database()


class TestGetAllProducts:
    """Test retrieving all products"""
    
    def test_get_all_products_returns_list(self):
        """Test that get_all_products returns a list"""
        products = get_all_products()
        assert isinstance(products, list)
    
    def test_get_all_products_returns_initial_data(self):
        """Test that initial database has products"""
        products = get_all_products()
        assert len(products) == 5  # Initial seed data has 5 products


class TestGetProductById:
    """Test retrieving product by ID"""
    
    def test_get_product_by_id_found(self):
        """Test getting existing product by ID"""
        product = get_product_by_id(1)
        assert product is not None
        assert product['id'] == 1
        assert product['product_name'] == 'Organic Almond Milk'
    
    def test_get_product_by_id_not_found(self):
        """Test getting non-existent product"""
        product = get_product_by_id(9999)
        assert product is None


class TestGetProductByName:
    """Test searching products by name"""
    
    def test_get_product_by_name_exact_match(self):
        """Test getting product by exact name"""
        products = get_product_by_name('Organic Almond Milk')
        assert len(products) == 1
        assert products[0]['product_name'] == 'Organic Almond Milk'
    
    def test_get_product_by_name_partial_match(self):
        """Test getting products by partial name"""
        products = get_product_by_name('milk')
        assert len(products) >= 1
        assert any('milk' in p['product_name'].lower() for p in products)
    
    def test_get_product_by_name_case_insensitive(self):
        """Test that search is case-insensitive"""
        products_lower = get_product_by_name('milk')
        products_upper = get_product_by_name('MILK')
        assert len(products_lower) == len(products_upper)


class TestGetProductByBarcode:
    """Test searching product by barcode"""
    
    def test_get_product_by_barcode_found(self):
        """Test getting product by barcode"""
        product = get_product_by_barcode('025005378348')
        assert product is not None
        assert product['id'] == 1
    
    def test_get_product_by_barcode_not_found(self):
        """Test getting non-existent barcode"""
        product = get_product_by_barcode('999999999999')
        assert product is None


class TestAddProduct:
    """Test adding products"""
    
    def test_add_product_success(self):
        """Test adding a new product"""
        initial_count = len(get_all_products())
        
        product_data = {
            "product_name": "New Product",
            "price": 5.99,
            "quantity": 20,
            "brands": "Test Brand"
        }
        
        new_product = add_product(product_data)
        
        assert new_product['product_name'] == 'New Product'
        assert new_product['price'] == 5.99
        assert len(get_all_products()) == initial_count + 1
    
    def test_add_product_auto_id(self):
        """Test that new product gets auto-incremented ID"""
        initial_count = len(get_all_products())
        
        product_data = {
            "product_name": "ID Test",
            "price": 1.0,
            "quantity": 1
        }
        
        new_product = add_product(product_data)
        
        assert new_product['id'] == initial_count + 1


class TestUpdateProduct:
    """Test updating products"""
    
    def test_update_product_price(self):
        """Test updating product price"""
        updated = update_product(1, {"price": 9.99})
        
        assert updated is not None
        assert updated['price'] == 9.99
        assert updated['product_name'] == 'Organic Almond Milk'  # Unchanged
    
    def test_update_product_quantity(self):
        """Test updating product quantity"""
        updated = update_product(1, {"quantity": 100})
        
        assert updated is not None
        assert updated['quantity'] == 100
    
    def test_update_product_multiple_fields(self):
        """Test updating multiple fields"""
        update_data = {
            "price": 7.99,
            "quantity": 50,
            "product_name": "New Name"
        }
        
        updated = update_product(1, update_data)
        
        assert updated['price'] == 7.99
        assert updated['quantity'] == 50
        assert updated['product_name'] == 'New Name'
    
    def test_update_product_not_found(self):
        """Test updating non-existent product"""
        updated = update_product(9999, {"price": 5.0})
        assert updated is None
    
    def test_update_product_persists(self):
        """Test that updates persist"""
        update_product(1, {"price": 8.88})
        product = get_product_by_id(1)
        
        assert product['price'] == 8.88


class TestDeleteProduct:
    """Test deleting products"""
    
    def test_delete_product_success(self):
        """Test deleting a product"""
        initial_count = len(get_all_products())
        
        success = delete_product(1)
        
        assert success is True
        assert len(get_all_products()) == initial_count - 1
    
    def test_delete_product_not_found(self):
        """Test deleting non-existent product"""
        success = delete_product(9999)
        assert success is False
    
    def test_delete_product_really_deleted(self):
        """Test that deleted product cannot be retrieved"""
        delete_product(1)
        product = get_product_by_id(1)
        
        assert product is None


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
