"""
Unit tests for OpenFoodFacts API Service
Tests external API integration with mocked responses
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.openfoodfacts_service import OpenFoodFactsService, get_service


@pytest.fixture
def service():
    """Create service instance"""
    return OpenFoodFactsService(timeout=5)


class TestOpenFoodFactsServiceBarcode:
    """Test barcode search functionality"""
    
    @patch('app.services.openfoodfacts_service.requests.Session.get')
    def test_get_product_by_barcode_success(self, mock_get, service):
        """Test successful barcode product fetch"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Milk",
                "brands": "Test Brand",
                "code": "123456789",
                "ingredients_text": "Milk, water",
                "categories": "Beverages",
                "nutriments": {
                    "energy-kcal_100g": 60,
                    "fat_100g": 3.5,
                    "proteins_100g": 3.2,
                    "carbohydrates_100g": 4.7
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = service.get_product_by_barcode("123456789")
        
        assert result is not None
        assert result['product_name'] == "Test Milk"
        assert result['brands'] == "Test Brand"
        assert result['nutrition_facts']['calories'] == 60
    
    @patch('app.services.openfoodfacts_service.requests.Session.get')
    def test_get_product_by_barcode_not_found(self, mock_get, service):
        """Test barcode product not found"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": 0, "product": {}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = service.get_product_by_barcode("999999999")
        
        assert result is None


class TestOpenFoodFactsServiceSearch:
    """Test product search functionality"""
    
    @patch('app.services.openfoodfacts_service.requests.Session.get')
    def test_search_products_success(self, mock_get, service):
        """Test successful product search"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "products": [
                {
                    "product_name": "Product 1",
                    "brands": "Brand 1",
                    "code": "111111111",
                    "ingredients_text": "Ingredients 1",
                    "categories": "Category 1",
                    "nutriments": {
                        "energy-kcal_100g": 100
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = service.search_products("test", limit=10)
        
        assert len(results) == 1
        assert results[0]['product_name'] == "Product 1"
    
    @patch('app.services.openfoodfacts_service.requests.Session.get')
    def test_search_products_empty_results(self, mock_get, service):
        """Test search with no results"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"products": []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        results = service.search_products("xyz", limit=10)
        
        assert len(results) == 0


class TestServiceSingleton:
    """Test singleton service pattern"""
    
    def test_get_service_returns_singleton(self):
        """Test get_service returns same instance"""
        service1 = get_service()
        service2 = get_service()
        
        assert service1 is service2
    
    def test_get_service_instance_is_correct_type(self):
        """Test get_service returns correct type"""
        service = get_service()
        
        assert isinstance(service, OpenFoodFactsService)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
