"""
OpenFoodFacts API Service
Handles integration with OpenFoodFacts API to fetch real product data
"""

import requests
from typing import Optional, Dict, Any

# OpenFoodFacts API endpoints
OPENFOODFACTS_API_URL = "https://world.openfoodfacts.org/api/v0/product"
OPENFOODFACTS_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


class OpenFoodFactsService:
    """Service for interacting with OpenFoodFacts API"""
    
    def __init__(self, timeout: int = 10):
        """Initialize the service with timeout setting"""
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'InventoryManagementSystem/1.0'
        })
    
    def get_product_by_barcode(self, barcode: str) -> Optional[Dict[str, Any]]:
        """
        Fetch product data from OpenFoodFacts by barcode
        
        Args:
            barcode: Product barcode
            
        Returns:
            Product data dict or None if not found
        """
        try:
            url = f"{OPENFOODFACTS_API_URL}/{barcode}.json"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("status") == 1:  # Status 1 means product found
                product = data.get("product", {})
                return self._extract_product_info(product)
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching from OpenFoodFacts: {str(e)}")
            return None
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return None
    
    def search_products(self, query: str, limit: int = 10) -> list:
        """
        Search for products on OpenFoodFacts
        
        Args:
            query: Search query (product name or brand)
            limit: Maximum number of results
            
        Returns:
            List of product data dicts
        """
        try:
            params = {
                'search_terms': query,
                'json': 1,
                'page_size': limit
            }
            
            response = self.session.get(
                OPENFOODFACTS_SEARCH_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            products = []
            
            for product in data.get("products", [])[:limit]:
                extracted = self._extract_product_info(product)
                if extracted:
                    products.append(extracted)
            
            return products
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching OpenFoodFacts: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []
    
    def _extract_product_info(self, product_data: Dict) -> Dict[str, Any]:
        """
        Extract relevant product information from OpenFoodFacts response
        
        Args:
            product_data: Raw product data from API
            
        Returns:
            Standardized product information
        """
        # Extract nutrition facts
        nutrition_facts = {}
        if "nutriments" in product_data:
            nutriments = product_data.get("nutriments", {})
            nutrition_facts = {
                "calories": nutriments.get("energy-kcal_100g", 0),
                "fat": nutriments.get("fat_100g", 0),
                "protein": nutriments.get("proteins_100g", 0),
                "carbohydrates": nutriments.get("carbohydrates_100g", 0),
                "fiber": nutriments.get("fiber_100g", 0),
                "sugar": nutriments.get("sugars_100g", 0)
            }
        
        return {
            "product_name": product_data.get("product_name", "Unknown"),
            "brands": product_data.get("brands", ""),
            "barcode": product_data.get("code", ""),
            "ingredients_text": product_data.get("ingredients_text", ""),
            "nutrition_facts": nutrition_facts,
            "category": product_data.get("categories", "Other"),
            "quantity": 0,  # Will be set in inventory
            "price": 0.0  # Will be set in inventory
        }


# Singleton instance
_service_instance = None


def get_service() -> OpenFoodFactsService:
    """Get or create the OpenFoodFacts service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = OpenFoodFactsService()
    return _service_instance
