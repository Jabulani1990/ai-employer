import requests
import logging
from ai_workers.ai_property_manager.models import PropertyListing

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class JijiPublisher:
    """Handles property publishing to Jiji"""

    API_URL = "https://api.jiji.ng/v1/listings"  # Replace with actual endpoint
    API_KEY = "test_api_key"  # Replace with actual test key

    def __init__(self, property_id):
        self.property = PropertyListing.objects.get(id=property_id)

    def prepare_payload(self):
        """Formats property data for Jiji API"""
        return {
            "title": self.property.title,
            "price": self.property.price,
            "location": self.property.location,
            "description": self.property.description,
            "category": "real-estate",  # Adjust as needed
            "images": self.get_images(),
        }

    def get_images(self):
        """Fetches property images (if any)"""
        return [img.url for img in self.property.images.all()]  # Assuming a related Image model

    def publish(self):
        """Sends property listing to Jiji"""
        headers = {"Authorization": f"Bearer {self.API_KEY}"}

        try:
            response = requests.post(self.API_URL, json=self.prepare_payload(), headers=headers)
            response_data = response.json()

            if response.status_code == 201:
                self.property.is_published_on_jiji = True
                self.property.jiji_listing_id = response_data.get("id")
                self.property.save()
                logging.info(f"Successfully published to Jiji: {self.property.title}")
                return {"status": "success", "message": "Property published on Jiji"}

            else:
                logging.error(f"Jiji publishing failed: {response_data}")
                return {"status": "error", "message": response_data}

        except requests.RequestException as e:
            logging.error(f"Jiji API request error: {str(e)}")
            return {"status": "error", "message": str(e)}


class FacebookMarketplacePublisher:
    """Handles property publishing to Facebook Marketplace"""

    API_URL = "https://graph.facebook.com/v18.0/{PAGE_ID}/marketplace_listings"  # Replace {PAGE_ID} with test page ID
    ACCESS_TOKEN = "test_access_token"  # Replace with actual test token

    def __init__(self, property_id):
        self.property = PropertyListing.objects.get(id=property_id)

    def prepare_payload(self):
        """Formats property data for Facebook Marketplace API"""
        return {
            "name": self.property.title,
            "price": self.property.price,
            "category_id": 105,  # Category ID for real estate
            "location": self.property.location,
            "description": self.property.description,
            "availability": "in stock",
            "condition": "new",
            "images": self.get_images(),
            "currency": "NGN",  # Adjust currency as needed
        }

    def get_images(self):
        """Fetches property images (if any)"""
        return [img.url for img in self.property.images.all()]  # Assuming a related Image model

    def publish(self):
        """Sends property listing to Facebook Marketplace"""
        headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}
        payload = self.prepare_payload()

        try:
            response = requests.post(self.API_URL, json=payload, headers=headers)
            response_data = response.json()

            if response.status_code == 200:
                self.property.is_published_on_facebook = True
                self.property.facebook_listing_id = response_data.get("id")
                self.property.save()
                logging.info(f"Successfully published to Facebook Marketplace: {self.property.title}")
                return {"status": "success", "message": "Property published on Facebook Marketplace"}

            else:
                logging.error(f"Facebook publishing failed: {response_data}")
                return {"status": "error", "message": response_data}

        except requests.RequestException as e:
            logging.error(f"Facebook API request error: {str(e)}")
            return {"status": "error", "message": str(e)}