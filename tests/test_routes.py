"""
Unit tests for Flask API endpoints
Tests CRUD operations and error handling
"""

import pytest
import json
from app import create_app
from app.database import mock_db


@pytest.fixture
def app():
    """Create and configure app for testing"""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(autouse=True)
def reset_db():
    """Reset database before each test"""
    mock_db.reset_database()
    yield
    mock_db.reset_database()


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns 200"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestGetProducts:
    """Test GET endpoints"""
    
    def test_get_all_products(self, client):
        """Test getting all products"""
        response = client.get('/api/products')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'count' in data
        assert 'data' in data
        assert isinstance(data['data'], list)
    
    def test_get_all_products_count(self, client):
        """Test getting all products returns correct count"""
        response = client.get('/api/products')
        data = json.loads(response.data)
        assert data['count'] == len(mock_db.get_all_products())
    
    def test_get_product_by_id(self, client):
        """Test getting specific product by ID"""
        response = client.get('/api/products/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['id'] == 1
        assert data['data']['product_name'] == 'Organic Almond Milk'
    
    def test_get_product_invalid_id(self, client):
        """Test getting non-existent product"""
        response = client.get('/api/products/9999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'


class TestCreateProduct:
    """Test POST endpoints"""
    
    def test_create_product_success(self, client):
        """Test creating a new product"""
        product_data = {
            "product_name": "Test Product",
            "price": 9.99,
            "quantity": 10,
            "brands": "Test Brand",
            "category": "Test"
        }
        response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['product_name'] == 'Test Product'
        assert data['data']['price'] == 9.99
    
    def test_create_product_missing_name(self, client):
        """Test creating product without name"""
        product_data = {
            "price": 9.99,
            "quantity": 10
        }
        response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_create_product_missing_price(self, client):
        """Test creating product without price"""
        product_data = {
            "product_name": "Test",
            "quantity": 10
        }
        response = client.post(
            '/api/products',
            data=json.dumps(product_data),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_create_product_no_json(self, client):
        """Test creating product with no JSON data"""
        response = client.post('/api/products')
        assert response.status_code == 400


class TestUpdateProduct:
    """Test PATCH endpoints"""
    
    def test_update_product_price(self, client):
        """Test updating product price"""
        update_data = {"price": 5.99}
        response = client.patch(
            '/api/products/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['price'] == 5.99
    
    def test_update_product_quantity(self, client):
        """Test updating product quantity"""
        update_data = {"quantity": 100}
        response = client.patch(
            '/api/products/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['quantity'] == 100
    
    def test_update_product_multiple_fields(self, client):
        """Test updating multiple fields"""
        update_data = {
            "price": 7.99,
            "quantity": 50,
            "product_name": "Updated Name"
        }
        response = client.patch(
            '/api/products/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['data']['price'] == 7.99
        assert data['data']['quantity'] == 50
        assert data['data']['product_name'] == 'Updated Name'
    
    def test_update_product_invalid_id(self, client):
        """Test updating non-existent product"""
        update_data = {"price": 5.99}
        response = client.patch(
            '/api/products/9999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 404


class TestDeleteProduct:
    """Test DELETE endpoints"""
    
    def test_delete_product_success(self, client):
        """Test deleting a product"""
        response = client.delete('/api/products/1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_delete_product_invalid_id(self, client):
        """Test deleting non-existent product"""
        response = client.delete('/api/products/9999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['status'] == 'error'
    
    def test_delete_product_really_deleted(self, client):
        """Test that deleted product is actually removed"""
        client.delete('/api/products/1')
        
        # Try to fetch deleted product
        response = client.get('/api/products/1')
        assert response.status_code == 404


class TestSearchByName:
    """Test name search endpoint"""
    
    def test_search_by_name_found(self, client):
        """Test searching for existing product"""
        response = client.get('/api/products/search/name?query=milk')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['count'] > 0
    
    def test_search_by_name_case_insensitive(self, client):
        """Test search is case-insensitive"""
        response1 = client.get('/api/products/search/name?query=milk')
        response2 = client.get('/api/products/search/name?query=MILK')
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        assert data1['count'] == data2['count']
    
    def test_search_by_name_not_found(self, client):
        """Test searching for non-existent product"""
        response = client.get('/api/products/search/name?query=xyzabc123')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['count'] == 0


class TestSearchByBarcode:
    """Test barcode search endpoint"""
    
    def test_search_by_barcode_found(self, client):
        """Test searching for existing barcode"""
        response = client.get('/api/products/search/barcode?barcode=025005378348')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['id'] == 1
    
    def test_search_by_barcode_not_found(self, client):
        """Test searching for non-existent barcode"""
        response = client.get('/api/products/search/barcode?barcode=999999999999')
        assert response.status_code == 404


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
